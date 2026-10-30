"""Read-only FM26 scouting, with calculations independent of the save decoder."""

import hashlib
import json
import shutil
import sqlite3
import tempfile
import unicodedata
import warnings
from calendar import monthrange
from datetime import date
from statistics import fmean
from pathlib import Path

import fmsave
from club_debt import read_current_club_debts
from club_finances import read_current_club_finances
from club_locations import read_current_club_links, read_installed_names, stadium_reference_fields
from fmsave.readers.competitions import find_competition_id_pair_layout, locate_competition_database_ids
from contract_reader import RELEASE_KINDS, contract_state, listing_status
from player_values import market_value_fields
from value_model import enrich_estimates
from staff_roles import ROLES as STAFF_ROLES
from staff_skills import SKILLS as STAFF_SKILLS, SCORING_SKILLS as STAFF_SCORING_SKILLS, enrich_staff_skills

NATION_NAMES = {int(key): value for key, value in json.loads((Path(__file__).parent / 'nation-names.json').read_text()).items()}
_CLUB_GENDERS = json.loads((Path(__file__).parent / 'club-genders.json').read_text())
FEMALE_CLUB_IDS = frozenset(_CLUB_GENDERS['female_ids'])
MALE_CLUB_IDS = frozenset(_CLUB_GENDERS['male_ids'])
STAFF_AREAS = {'medical':'Área médica','coaching':'Comissão técnica','recruitment':'Recrutamento','manager':'Treinador (humano)','unknown':'Área não identificada'}
REGIONS = {'africa':'África', 'asia':'Ásia', 'europe':'Europa',
           'north_america':'América do Norte, Central e Caribe', 'south_america':'América do Sul', 'oceania':'Oceania'}
NATION_REGIONS = {n: region for start, end, region in ((0,50,'africa'),(51,91,'asia'),(92,120,'north_america'),
                 (126,176,'europe'),(177,186,'oceania'),(187,196,'south_america'))
                 for n in range(start,end+1) if n in NATION_NAMES}
NATION_REGIONS.update({128:'asia',130:'asia',136:'asia',144:'asia',149:'asia',173:'asia',105:'south_america',117:'south_america',
    197:'asia',201:'oceania',202:'asia',203:'oceania',204:'africa',205:'north_america',206:'north_america',207:'north_america',
    208:'north_america',209:'north_america',210:'oceania',211:'asia',212:'north_america',215:'oceania',216:'europe',
    217:'north_america',218:'europe',219:'europe',225:'south_america',226:'north_america',227:'north_america',
    228:'north_america',229:'north_america',230:'africa',231:'africa',232:'oceania',233:'north_america',234:'africa',
    236:'asia',239:'africa',240:'africa',242:'oceania',243:'oceania',244:'oceania',247:'europe',249:'north_america'})
EU_NATIONS = {129,131,134,135,136,137,138,140,142,143,145,146,147,150,151,153,154,156,158,161,162,163,164,168,169,170,171}


def nationality_fields(row):
    ids = list(dict.fromkeys(n for n in [row.get('nation_id'), *(row.get('second_nation_ids') or [])] if n is not None))
    row['nation_ids'] = ids
    row['nationalities'] = [{'id': n, 'name': NATION_NAMES.get(n), 'is_eu': n in EU_NATIONS if n in NATION_NAMES else None} for n in ids]
    row['nation_name'] = ', '.join(NATION_NAMES.get(n, 'Nome indisponível') for n in ids) if any(n in NATION_NAMES for n in ids) else None
    row['nation_regions'] = sorted({NATION_REGIONS[n] for n in ids if n in NATION_REGIONS})
    row['eu_national'] = True if any(n in EU_NATIONS for n in ids) else False if row.get('nation_id') in NATION_NAMES and all(n in NATION_NAMES for n in ids) else None

TECHNICAL = {
    'corners': 'Escanteios', 'crossing': 'Cruzamentos', 'dribbling': 'Drible',
    'finishing': 'Finalização', 'first_touch': 'Primeiro toque',
    'free_kick_taking': 'Faltas', 'heading': 'Cabeceio', 'long_shots': 'Chutes de longe',
    'long_throws': 'Arremessos laterais', 'marking': 'Marcação', 'passing': 'Passe',
    'penalty_taking': 'Pênaltis', 'tackling': 'Desarme', 'technique': 'Técnica',
}
MENTAL = {
    'aggression': 'Agressividade', 'anticipation': 'Antecipação', 'bravery': 'Coragem',
    'composure': 'Compostura', 'concentration': 'Concentração', 'decisions': 'Decisões',
    'determination': 'Determinação', 'flair': 'Imprevisibilidade', 'leadership': 'Liderança',
    'off_the_ball': 'Sem bola', 'positioning': 'Posicionamento', 'teamwork': 'Trabalho em equipe',
    'vision': 'Visão', 'work_rate': 'Índice de trabalho',
}
PHYSICAL = {
    'acceleration': 'Aceleração', 'agility': 'Agilidade', 'balance': 'Equilíbrio',
    'jumping_reach': 'Impulsão', 'natural_fitness': 'Aptidão física', 'pace': 'Velocidade',
    'stamina': 'Resistência', 'strength': 'Força',
}
GOALKEEPING = {
    'aerial_reach': 'Alcance aéreo', 'command_of_area': 'Comando da área',
    'communication': 'Comunicação', 'eccentricity': 'Excentricidade', 'handling': 'Mãos',
    'kicking': 'Pontapé', 'one_on_ones': 'Um contra um', 'punching': 'Socos',
    'reflexes': 'Reflexos', 'rushing_out': 'Saídas', 'throwing': 'Lançamentos',
}
HIDDEN = {
    'consistency': 'Consistência', 'important_matches': 'Jogos importantes',
    'injury_proneness': 'Propensão a lesões', 'dirtiness': 'Jogo sujo', 'versatility': 'Versatilidade',
}
PERSONALITY = {
    'adaptability': 'Adaptabilidade', 'ambition': 'Ambição', 'loyalty': 'Lealdade',
    'pressure': 'Pressão', 'professionalism': 'Profissionalismo', 'sportsmanship': 'Fair play',
    'temperament': 'Temperamento', 'controversy': 'Controvérsia',
}
SUM_FIELDS = tuple(TECHNICAL) + tuple(MENTAL) + tuple(PHYSICAL)
POSITIONS = {'GK', 'SW', 'DL', 'DC', 'DR', 'DM', 'ML', 'MC', 'MR', 'AML', 'AMC', 'AMR', 'STC', 'WBL', 'WBR'}
RANGES = {'age': 100, 'ca': 200, 'pa': 200, 'ability_difference': 200, 'sum': 720,
          'rating': 100, 'rep_home': 10000, 'rep_current': 10000, 'rep_world': 10000,
          'club_reputation': 10000, 'reputation': 10000, 'value': 10**12, 'wage': 10**12,
          'release_fee': 10**12, 'balance': 10**12, 'transfer_budget_remaining': 10**12,
          'wage_budget_weekly': 10**12, 'height_cm': 255,
          'stadium_seated_capacity': 1000000, 'stadium_expansion_capacity': 1000000,
          'model_value': 10**12, 'model_fee': 10**12}


def contract_fields(row):
    c = row.get('contract') or {}
    row['wage'] = c.get('wage', row.get('wage'))
    row['contract_start'] = c.get('start', row.get('contract_start'))
    row['contract_end'] = c.get('end', row.get('contract_end'))
    row['squad_status_code'] = c.get('squad_status_code')
    row['contract_kind_code'] = c.get('kind_code')
    clauses = c.get('clauses') or []
    row['release_kinds'] = [clause['kind'] for clause in clauses if clause['kind'] in RELEASE_KINDS]
    for column, clause_kind in (('release_fee', 'minimum_fee_release'),
                                ('release_fee_domestic', 'minimum_fee_release_domestic'),
                                ('release_fee_foreign', 'minimum_fee_release_foreign')):
        fees = [clause['value'] for clause in clauses if clause['kind'] == clause_kind
                and clause.get('parameter') is None and clause.get('value') is not None]
        row[column] = min(fees) if fees else None
    row['contract_state'] = contract_state(row)
    if 'contract' in row and (row['contract_state'] != 'contracted' or c.get('end_source') != 'contract'):
        row['contract_start'] = row['contract_end'] = None
    row['has_contract_data'] = row['contract_state'] == 'contracted' or row.get('has_contract', False)
    return row
GROUPS = {'Técnicos': TECHNICAL, 'Mentais': MENTAL, 'Físicos': PHYSICAL,
          'Goleiro': GOALKEEPING, 'Ocultos': HIDDEN, 'Personalidade': PERSONALITY,
          'Profissionais': {key: label for key, (_, label) in STAFF_SKILLS.items()}}

# These are our transparent scouting weights, not Genie's proprietary ratings.
ROLES = {
    'GK': ('Goleiro', 'gk', {'reflexes': 3, 'handling': 2, 'one_on_ones': 2, 'aerial_reach': 2, 'positioning': 2, 'decisions': 1}),
    'DC': ('Zagueiro', 'dc', {'marking': 3, 'tackling': 3, 'positioning': 3, 'heading': 2, 'jumping_reach': 2, 'strength': 2, 'concentration': 2, 'pace': 1}),
    'DL': ('Lateral esquerdo', 'dl', {'tackling': 2, 'positioning': 2, 'crossing': 2, 'pace': 2, 'stamina': 2, 'work_rate': 2, 'passing': 1}),
    'DR': ('Lateral direito', 'dr', {'tackling': 2, 'positioning': 2, 'crossing': 2, 'pace': 2, 'stamina': 2, 'work_rate': 2, 'passing': 1}),
    'DM': ('Volante', 'dm', {'tackling': 3, 'positioning': 3, 'anticipation': 2, 'passing': 2, 'decisions': 2, 'teamwork': 2, 'stamina': 1}),
    'MC': ('Meio-campista', 'mc', {'passing': 3, 'vision': 2, 'decisions': 2, 'first_touch': 2, 'teamwork': 2, 'stamina': 2, 'technique': 1}),
    'AMC': ('Meia ofensivo', 'amc', {'vision': 3, 'passing': 3, 'technique': 2, 'first_touch': 2, 'decisions': 2, 'off_the_ball': 2, 'dribbling': 1}),
    'AML': ('Ponta esquerdo', 'aml', {'dribbling': 3, 'acceleration': 3, 'pace': 2, 'crossing': 2, 'off_the_ball': 2, 'technique': 1}),
    'AMR': ('Ponta direito', 'amr', {'dribbling': 3, 'acceleration': 3, 'pace': 2, 'crossing': 2, 'off_the_ball': 2, 'technique': 1}),
    'STC': ('Atacante', 'stc', {'finishing': 3, 'off_the_ball': 3, 'composure': 2, 'anticipation': 2, 'acceleration': 2, 'first_touch': 1}),
}


def attribute_sum(attributes, fields=SUM_FIELDS):
    values = [attributes.get(key) for key in fields]
    if not all(type(v) is int and 1 <= v <= 20 for v in values):
        return None
    return sum(values)


def records(table):
    return json.loads(json.dumps(table.to_dicts(), default=date.isoformat, allow_nan=False))


def role_score(player, role):
    _, position, weights = ROLES[role]
    attrs = player.get('attributes', {})
    familiarity = player.get('positions', {}).get(position)
    if familiarity is None or any(attrs.get(k) is None for k in weights):
        return None
    base = sum(attrs[k] * w for k, w in weights.items()) / sum(weights.values()) * 5
    return round(base * (0.75 + 0.25 * familiarity / 20), 1)


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text or '')).casefold()
                   if not unicodedata.combining(c))


def column_value(row, column):
    if column.startswith('attr_'):
        key = column[5:]
        if 'professional_attributes' in row and key in STAFF_SKILLS:
            return row.get('professional_attributes', {}).get(key)
        return (row.get('personality' if key in PERSONALITY else 'attributes') or {}).get(key)
    return row.get(column)


def squad_metrics(players):
    result = {'player_count': len(players)}
    for key in ('ca', 'pa', 'age'):
        values = [p[key] for p in players if p.get(key) is not None]
        result[f'{key}_mean'] = fmean(values) if values else None
        result[f'{key}_count'] = len(values)
    return result


def club_squads(clubs, players):
    members = {}
    for player in players:
        if player.get('club_uid') is not None:
            members.setdefault(player['club_uid'], []).append(player)
    for club in clubs:
        all_players = members.get(club['uid'], [])
        club['squad_metrics'] = {'all': squad_metrics(all_players),
                                 'first': squad_metrics([p for p in all_players if p.get('team_slot') == 0])}


def exclude_female_clubs(clubs, players, staff):
    hidden = set()
    for club in clubs:
        # fmsave 0.5.10 exposes the closing database identifier with +1.
        database_id = club['unique_id'] - 1 if club.get('unique_id') is not None else None
        club['gender'] = 'female' if database_id in FEMALE_CLUB_IDS else 'male' if database_id in MALE_CLUB_IDS else None
        if club['gender'] == 'female':
            hidden.add(club['uid'])
    return ([c for c in clubs if c['uid'] not in hidden],
            [p for p in players if p.get('club_uid') not in hidden],
            [s for s in staff if s.get('club_uid') not in hidden], len(hidden))


def club_stadium_fields(clubs, stadiums, links=None, grounds=None):
    homes = {}
    for stadium in stadiums:
        for uid in stadium.get('home_club_uids', ()):
            homes.setdefault(uid, []).append(stadium)
    for club in clubs:
        ground = (grounds or {}).get((links or {}).get(club['uid'], {}).get('stadium_ordinal'))
        if ground is not None:
            club.update(ground, stadium_source='club_status')
            continue
        matches = homes.get(club['uid'], [])
        # Ownership is not the stadium used for home matches; multiple grounds remain ambiguous.
        if len(matches) == 1:
            ground = matches[0]
            club.update(stadium_name=ground.get('name'),
                        stadium_seated_capacity=ground.get('all_seater_capacity'),
                        stadium_expansion_capacity=ground.get('expansion_capacity'))


def club_league_fields(clubs, competitions, tables, names, links=None, database_ids=None, table_names=None):
    by_id = {c['id']: c for c in competitions}
    choices = {}
    for table in tables:
        competition = by_id.get(table.get('competition_id'), {})
        database_id = competition.get('database_id')
        if database_id not in (names if table_names is None else table_names):
            continue
        for row in table['rows']:
            if row.get('team_slot') == 0 and row.get('club_uid') is not None:
                choices.setdefault(row['club_uid'], set()).add(database_id)
    for club in clubs:
        ids = choices.get(club['uid'], set())
        current = (database_ids or {}).get((links or {}).get(club['uid'], {}).get('current_competition_id'))
        if current in names:
            ids = {current}
            club['league_source'] = 'club_status'
        club['league_key'] = f'db:{next(iter(ids))}' if len(ids) == 1 else None
        club['league_name'] = names[next(iter(ids))] if len(ids) == 1 else None
    present = {c['league_key']: c['league_name'] for c in clubs if c['league_key']}
    return [{'key': key, 'name': name} for key, name in sorted(present.items(), key=lambda pair: pair[1])]


def staff_fields(member):
    areas = ['manager'] if member.get('is_human_manager') else [key for index,key in enumerate(('medical','coaching','recruitment')) if index in member.get('list_indexes', ())]
    member['staff_area_keys'] = areas or ['unknown']
    member['staff_area'] = ', '.join(STAFF_AREAS[key] for key in member['staff_area_keys'])
    member['staff_role_key'] = 'human_manager' if member.get('is_human_manager') else 'unknown'
    member['staff_role'] = STAFF_ROLES[member['staff_role_key']]
    member['attribute_sum'] = None


def enrich(player):
    nationality_fields(player)
    attrs = player.get('attributes', {})
    player['attribute_sum'] = attribute_sum(attrs)
    player['technical_sum'] = attribute_sum(attrs, tuple(TECHNICAL))
    player['mental_sum'] = attribute_sum(attrs, tuple(MENTAL))
    player['physical_sum'] = attribute_sum(attrs, tuple(PHYSICAL))
    player['goalkeeping_sum'] = attribute_sum(attrs, tuple(GOALKEEPING))
    player['ca'] = (player.get('ability') or {}).get('current')
    player['pa'] = (player.get('ability') or {}).get('potential')
    player['ability_difference'] = player['pa'] - player['ca'] if player['pa'] is not None and player['ca'] is not None else None
    for field in ('home', 'current', 'world'):
        player[f'rep_{field}'] = (player.get('reputation') or {}).get(field)
    market_value_fields(player)
    contract_fields(player)
    player['roles'] = {key: role_score(player, key) for key in ROLES}
    familiar = [(key, value) for key, value in player['roles'].items()
                if value is not None and (player.get('positions', {}).get(ROLES[key][1]) or 0) >= 15]
    best = max(familiar, key=lambda r: r[1], default=(None, None))
    player['best_role'], player['rating'] = best
    return player


def filter_rows(rows, query, shortlist=(), game_date=None):
    kind = query.get('kind', 'players')
    results = []
    search = normalized(query.get('search', ''))
    numeric_choices = {key: set(map(int, query[key].split(','))) for key in ('club','nation','based','squad_status','contract_kind') if query.get(key)}
    positions = set(query.get('position','').split(',')) - {''}
    leagues = set(query.get('league','').split(',')) - {''}
    release_kinds = set(query.get('release_kind','').split(',')) - {''}
    availability = query.get('availability')
    today = date.fromisoformat(game_date) if game_date else None
    deadline = None
    if availability in ('expiring_6', 'expiring_12') and today:
        year, month = divmod(today.year * 12 + today.month - 1 + int(availability.split('_')[1]), 12)
        deadline = date(year, month + 1, min(today.day, monthrange(year, month + 1)[1])).isoformat()
    for row in rows:
        if availability == 'free' and row.get('contract_state') != 'free':
            continue
        if availability in ('transfer_listed', 'loan_listed') and row.get(availability) is not True:
            continue
        if availability in ('expiring_6', 'expiring_12'):
            contract = row.get('contract') or {}
            expiry = row.get('contract_end')
            if (not deadline or row.get('contract_state') != 'contracted'
                    or contract.get('end_source') != 'contract' or not expiry
                    or not contract.get('start') or contract['start'] > today.isoformat()
                    or not today.isoformat() <= expiry <= deadline):
                continue
        if search and search not in normalized(f"{row.get('name', '')} {row.get('short_name', '')} {row.get('club_name', '')} {row.get('club_short_name', '')}"):
            continue
        if 'club' in numeric_choices and row.get('club_uid') not in numeric_choices['club']:
            continue
        if query.get('staff_role') and row.get('staff_role_key') not in query['staff_role'].split(','):
            continue
        if query.get('staff_area') and not set(query['staff_area'].split(',')).intersection(row.get('staff_area_keys', ())):
            continue
        if query.get('squad') == 'first' and row.get('team_slot') != 0:
            continue
        if query.get('squad') == 'other' and (row.get('team_slot') is None or row['team_slot'] <= 0):
            continue
        if 'nation' in numeric_choices and not numeric_choices['nation'].intersection(row.get('nation_ids', [row.get('nation_id')])):
            continue
        if leagues and row.get('league_key') not in leagues:
            continue
        if query.get('nation_region') and not set(query['nation_region'].split(',')).intersection(row.get('nation_regions', [])):
            continue
        if query.get('eu_national') and row.get('eu_national') is not (query['eu_national'] == 'yes'):
            continue
        if query.get('based_region') and row.get('club_region') not in query['based_region'].split(','):
            continue
        if (query.get('shortlist') == '1' or query.get('within_shortlist') == '1') and row['uid'] not in shortlist:
            continue
        if kind == 'players' and positions and not any((row.get('positions', {}).get(position.lower()) or 0) >= 15 for position in positions):
            continue
        if query.get('free') == '1' and row.get('contract_state') != 'free':
            continue
        failed = False
        for field in RANGES:
            actual = row.get('attribute_sum' if field == 'sum' else field)
            if field == 'release_fee' and release_kinds:
                fees = [c['value'] for c in (row.get('contract') or {}).get('clauses', [])
                        if c.get('kind') in release_kinds and c.get('value') is not None]
                actual = min(fees) if fees else None
            for bound in ('min', 'max'):
                value = query.get(f'{field}_{bound}')
                if value and (actual is None or isinstance(actual, dict) or (actual < float(value) if bound == 'min' else actual > float(value))):
                    failed = True
                    break
            if failed:
                break
        if failed:
            continue
        if query.get('contract_before'):
            expiry = row.get('contract_end')
            if expiry is None or expiry > query['contract_before']:
                continue
        if query.get('contract_after'):
            expiry = row.get('contract_end')
            if expiry is None or expiry < query['contract_after']:
                continue
        if query.get('no_contract') == '1' and not (row.get('contract_state') == 'free'
                or kind == 'staff' and row.get('has_contract') is False
                and not row.get('has_club_appointment')):
            continue
        if 'squad_status' in numeric_choices and row.get('squad_status_code') not in numeric_choices['squad_status']:
            continue
        if 'contract_kind' in numeric_choices and row.get('contract_kind_code') not in numeric_choices['contract_kind']:
            continue
        if release_kinds and not release_kinds.intersection(row.get('release_kinds', [])):
            continue
        if query.get('has_release') == '1' and not row.get('release_kinds'):
            continue
        if 'based' in numeric_choices and row.get('club_nation_id') not in numeric_choices['based']:
            continue
        if query.get('traits') and not set(map(int, query['traits'].split(','))).issubset(row.get('traits_code', [])):
            continue
        for field, value in query.items():
            if (field.startswith('attr_') or field.startswith('maxattr_')) and value:
                maximum = field.startswith('maxattr_')
                key = field.removeprefix('maxattr_' if maximum else 'attr_')
                attr = column_value(row, 'attr_' + key)
                if attr is None or (attr > float(value) if maximum else attr < float(value)):
                    failed = True
                    break
        if not failed:
            results.append(row)
    sort = query.get('sort', 'pa' if kind != 'clubs' else 'reputation')
    valid = {'name', 'age', 'club_name', 'ca', 'pa', 'attribute_sum', 'rating', 'reputation', 'nation_id', 'eu_national', 'goalkeeping_sum', 'ability_difference', 'rep_home', 'rep_current', 'rep_world', 'wage', 'value', 'release_fee', 'ca_mean', 'pa_mean', 'age_mean', 'player_count', 'ca_count', 'pa_count', 'age_count', 'team_slot'}
    attribute_columns = {f'attr_{key}' for group in GROUPS.values() for key in group}
    valid.update(('staff_area','staff_role','height_cm','balance','transfer_budget_remaining',
                  'wage_budget_weekly','league_name','stadium_name','stadium_seated_capacity','stadium_expansion_capacity',
                  'release_fee_domestic','release_fee_foreign','model_value','model_fee'))
    if sort not in valid | attribute_columns:
        raise ValueError('Coluna de ordenação inválida.')
    def sort_value(row):
        if sort == 'name' and kind == 'clubs':
            return row.get('short_name') or row.get('name')
        if sort == 'club_name':
            return row.get('club_short_name') or row.get('club_name')
        return row.get('nation_name') if sort == 'nation_id' else column_value(row, sort)
    def key(row):
        value = sort_value(row)
        if isinstance(value, str):
            value = normalized(value)
        return value, row.get('attribute_sum') or -1, normalized(row.get('name'))
    present = [r for r in results if sort_value(r) is not None]
    absent = [r for r in results if sort_value(r) is None]
    return sorted(present, key=key, reverse=query.get('direction', 'desc') == 'desc') + absent


class Scout:
    def __init__(self, storage):
        self.storage = Path(storage)
        self.storage.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS shortlist(career TEXT, kind TEXT, uid INTEGER,
                    PRIMARY KEY(career, kind, uid));
                CREATE TABLE IF NOT EXISTS snapshots(career TEXT, uid INTEGER, date TEXT,
                    attributes TEXT, ca INTEGER, pa INTEGER, birth_date TEXT, unique_id INTEGER,
                    PRIMARY KEY(career, uid, date));
            ''')
        self.rows = {'players': [], 'staff': [], 'clubs': []}
        self.index = {k: {} for k in self.rows}
        self.meta = None
        self.career = None
        self.competitions = []

    def db(self):
        return sqlite3.connect(self.storage)

    def load(self, path, progress=lambda message: None):
        source = Path(path).expanduser().resolve(strict=True)
        if not source.is_file() or source.suffix.lower() != '.fm':
            raise ValueError('Selecione um arquivo de save .fm do FM26.')
        career = hashlib.sha256(str(source).encode()).hexdigest()
        progress('Copiando o save para leitura…')
        before = source.stat()
        with tempfile.TemporaryDirectory(prefix='fm-matt-scout-') as temp:
            copy = Path(temp) / 'career.fm'
            shutil.copyfile(source, copy)
            after = source.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('O FM está salvando este arquivo. Aguarde terminar e abra novamente.')
            with warnings.catch_warnings(record=True) as captured, fmsave.open(copy) as save:
                progress('Lendo jogadores e atributos…')
                players = [enrich(p) for p in records(save.players())]
                for player in players:
                    player['transfer_listed'], player['loan_listed'] = listing_status(
                        player, save.info.build, str(save.info.game_date))
                progress('Lendo staff e clubes…')
                notes = []
                try:
                    staff = records(save.staff())
                except (fmsave.FmsaveError, ValueError) as exc:
                    staff = []
                    notes.append(f'Staff indisponível: {exc}')
                for member in staff:
                    staff_fields(member)
                    member['ca'] = member['ability']['current']
                    member['pa'] = member['ability']['potential']
                    member['ability_difference'] = member['pa'] - member['ca'] if member['pa'] is not None and member['ca'] is not None else None
                    contract_fields(member)
                clubs = records(save.clubs())
                try:
                    enrich_staff_skills(save, staff, clubs)
                except (fmsave.FmsaveError, ValueError) as exc:
                    notes.append(f'Atributos profissionais do staff indisponíveis: {exc}')
                clubs, players, staff, hidden_female_clubs = exclude_female_clubs(clubs, players, staff)
                for club in clubs:
                    club['club_uid'] = club['uid']
                    club['club_nation_id'] = club['nation_id']
                club_squads(clubs, players)
                club_index = {c['uid']: c for c in clubs}
                for member in staff:
                    club = club_index.get(member['club_uid'])
                    member['club_short_name'] = club.get('short_name') if club else None
                    member['club_reputation'] = club['reputation'] if club else None
                    member['club_nation_id'] = club['nation_id'] if club else None
                try:
                    finances = {}
                    for record in records(save.finances()):
                        previous = finances.get(record['club_uid'])
                        if record['month'] <= str(save.info.game_date) and (previous is None or record['month'] > previous['month']):
                            finances[record['club_uid']] = record
                    for club in clubs:
                        record = finances.get(club['uid'])
                        if record:
                            club.update({field: record[field] for field in ('balance', 'transfer_budget_remaining', 'wage_budget_weekly')})
                            club['finance_date'] = record['month']
                            club['finance_source'] = 'monthly'
                    with save._context.section('game_db') as game_db:
                        current_finances = read_current_club_finances(
                            game_db, save._context.own_club_record_spans(), save.info.build,
                            save.info.game_date, save.info.section_schemas.get('game_db'))
                    for club in clubs:
                        if club['uid'] in current_finances:
                            club.update(current_finances[club['uid']])
                except (fmsave.FmsaveError, ValueError) as exc:
                    notes.append(f'Finanças dos clubes indisponíveis: {exc}')
                progress('Lendo empréstimos financeiros…')
                try:
                    with save._context.section('game_db') as game_db:
                        debts = read_current_club_debts(
                            game_db, save._context.own_club_record_spans(), save.info.build)
                    for club in clubs:
                        if club['uid'] in debts:
                            club.update(debts[club['uid']])
                except (fmsave.FmsaveError, ValueError) as exc:
                    notes.append(f'Empréstimos financeiros indisponíveis: {exc}')
                installed_names = read_installed_names()
                links, database_ids = {}, {}
                try:
                    with save._context.section('game_db') as game_db:
                        links = read_current_club_links(game_db, save._context.own_club_record_spans(), save.info.build)
                        layout = find_competition_id_pair_layout(save.info.section_schemas.get('game_db'), save.info.build)
                        database_ids = locate_competition_database_ids(game_db, layout)
                except (fmsave.FmsaveError, ValueError) as exc:
                    notes.append(f'Vínculos atuais dos clubes indisponíveis: {exc}')
                try:
                    grounds = stadium_reference_fields(save._context.stadium_index(), installed_names.get('stadiums', {}))
                    club_stadium_fields(clubs, records(save.stadiums()), links, grounds)
                except (fmsave.FmsaveError, ValueError) as exc:
                    notes.append(f'Estádios indisponíveis: {exc}')
                progress('Lendo ligas e competições…')
                competitions = []
                try:
                    names = fmsave.read_competition_names(Path(__file__).parent / 'league-names.csv')
                    table_names = names
                    names = {**installed_names.get('competitions', {}), **names}
                    competitions = club_league_fields(clubs, records(save.competitions()),
                                                     records(save.league_tables()), names, links, database_ids, table_names)
                except (fmsave.FmsaveError, OSError, ValueError) as exc:
                    notes.append(f'Ligas indisponíveis: {exc}')
                for row in players + staff:
                    club = club_index.get(row.get('club_uid'), {})
                    row['league_key'] = club.get('league_key')
                    row['league_name'] = club.get('league_name')
                for row in players + staff + clubs:
                    nationality_fields(row)
                    row['club_nation_name'] = NATION_NAMES.get(row.get('club_nation_id'))
                    row['nation_region'] = NATION_REGIONS.get(row.get('nation_id'))
                    row['club_region'] = NATION_REGIONS.get(row.get('club_nation_id'))
                try:
                    managed = records(save.managed_clubs())
                except (fmsave.FmsaveError, ValueError) as exc:
                    managed = []
                    notes.append(f'Time do treinador não identificado: {exc}')
                buyer = club_index.get(managed[0]['club_uid'], {}) if len(managed) == 1 else {}
                enrich_estimates(players, str(save.info.game_date), buyer.get('reputation'))
                meta = {'file': source.name, 'path': str(source), 'date': str(save.info.game_date),
                        'build': save.info.build, 'managed': managed,
                        'counts': {'players': len(players), 'staff': len(staff), 'clubs': len(clubs)},
                        'hidden_female_clubs': hidden_female_clubs,
                        'listing_status_count': sum(type(p.get('transfer_listed')) is bool
                                                    and type(p.get('loan_listed')) is bool for p in players),
                        'league_clubs_count': sum(c.get('league_key') is not None for c in clubs),
                        'staff_roles_count': sum(s.get('staff_role_key') != 'unknown' for s in staff),
                        'staff_skills_count': sum(s.get('attribute_sum') is not None for s in staff),
                        'warnings': notes + [str(w.message) for w in captured],
                        'ability_status': fmsave.field_status(fmsave.Player, 'ability.current')}
        rows = {'players': players, 'staff': staff, 'clubs': clubs}
        progress('Registrando evolução dos jogadores…')
        with self.db() as db:
            db.executemany('INSERT OR IGNORE INTO snapshots VALUES(?,?,?,?,?,?,?,?)', [
                (career, p['uid'], meta['date'], json.dumps(p['attributes']), p['ca'], p['pa'],
                 p['birth_date'], p['unique_id']) for p in players])
        self.rows = rows
        self.index = {kind: {r['uid']: r for r in records} for kind, records in rows.items()}
        self.meta, self.career = meta, career
        self.competitions = competitions
        return meta

    def shortlisted(self, kind):
        with self.db() as db:
            return {r[0] for r in db.execute('SELECT uid FROM shortlist WHERE career=? AND kind=?', (self.career, kind))}

    def toggle_shortlist(self, kind, uid):
        if uid not in self.index[kind]:
            raise ValueError('Registro não encontrado neste save.')
        with self.db() as db:
            if uid in self.shortlisted(kind):
                db.execute('DELETE FROM shortlist WHERE career=? AND kind=? AND uid=?', (self.career, kind, uid))
                return False
            db.execute('INSERT INTO shortlist VALUES(?,?,?)', (self.career, kind, uid))
            return True

    def history(self, uid):
        player = self.index['players'][uid]
        with self.db() as db:
            return [{'date': date, 'ca': ca, 'pa': pa, 'attributes': json.loads(attrs),
                     'attribute_sum': attribute_sum(json.loads(attrs))}
                    for date, attrs, ca, pa in db.execute(
                        'SELECT date,attributes,ca,pa FROM snapshots WHERE career=? AND uid=? AND birth_date=? AND unique_id=? ORDER BY date',
                        (self.career, uid, player['birth_date'], player['unique_id']))]
