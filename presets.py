"""Portable, validated tactical filters. No save data is stored in these files."""

import json
import re
import secrets
from datetime import date
from pathlib import Path

from scout import GROUPS, POSITIONS, RANGES, RELEASE_KINDS, REGIONS, STAFF_AREAS, STAFF_ROLES, STAFF_SCORING_SKILLS

FIELDS = {'search', 'position', 'age_min', 'age_max', 'ca_min', 'pa_min', 'sum_min', 'availability',
          'rating_min', 'club', 'nation', 'league', 'contract_before', 'contract_after', 'free', 'sort', 'direction',
          'based', 'nation_region', 'based_region', 'eu_national', 'within_shortlist', 'no_contract', 'contract_kind', 'squad_status', 'release_kind', 'has_release', 'traits', 'squad_scope', 'squad','staff_area','staff_role'}
FIELDS.update(f'{field}_{bound}' for field in RANGES for bound in ('min', 'max'))
ATTRIBUTES = {key for group in GROUPS.values() for key in group}


def validate_filter(preset):
    if not isinstance(preset, dict):
        raise ValueError('Filtro inválido.')
    name = preset.get('name')
    kind = preset.get('kind')
    values = preset.get('filters')
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        raise ValueError('Dê um nome ao filtro (até 120 caracteres).')
    if kind not in ('players', 'staff', 'clubs') or not isinstance(values, dict):
        raise ValueError('Tipo de filtro inválido.')
    clean = {}
    for key, value in values.items():
        attribute = key.startswith(('attr_', 'maxattr_'))
        if key not in FIELDS and not (attribute and key.split('_', 1)[1] in ATTRIBUTES):
            raise ValueError(f'Condição desconhecida: {key}')
        if not isinstance(value, (str, int, float)) or isinstance(value, bool):
            raise ValueError(f'Valor inválido para {key}.')
        value = str(value)
        if len(value) > 2048:
            raise ValueError('Valor de filtro muito longo.')
        if not value:
            continue
        if key == 'availability' and (kind != 'players' or value not in
                ('free', 'expiring_6', 'expiring_12', 'transfer_listed', 'loan_listed')):
            raise ValueError('Filtro de disponibilidade inválido.')
        if key in ('nation_region','based_region'):
            if not set(value.split(',')).issubset(REGIONS):
                raise ValueError('Região inválida.')
            clean[key] = ','.join(dict.fromkeys(value.split(',')))
            continue
        if key == 'eu_national' and value not in ('yes','no'):
            raise ValueError('Filtro de nacionalidade UE inválido.')
        if key in ('staff_area', 'staff_role'):
            choices = STAFF_AREAS if key == 'staff_area' else STAFF_ROLES
            if kind != 'staff' or not set(value.split(',')).issubset(choices):
                raise ValueError('Área do staff inválida.')
            clean[key] = ','.join(dict.fromkeys(value.split(',')))
            continue
        if key in ('club', 'nation', 'based', 'contract_kind', 'squad_status'):
            if not re.fullmatch(r'\d+(,\d+)*', value) or any(int(v)>4294967295 for v in value.split(',')):
                raise ValueError(f'Opções inválidas: {key}.')
            clean[key] = ','.join(dict.fromkeys(value.split(',')))
            continue
        range_field = key.rsplit('_', 1)[0] if key.rsplit('_', 1)[-1] in ('min', 'max') else None
        if attribute or range_field in RANGES:
            number = float(value)
            ceiling = 20 if attribute else RANGES.get(range_field, 4294967295)
            if kind == 'staff' and range_field == 'sum':
                ceiling = len(STAFF_SCORING_SKILLS) * 20
            floor = -ceiling if range_field in ('balance', 'ability_difference') else 0
            if not floor <= number <= ceiling or (attribute and not 1 <= number <= 20):
                raise ValueError(f'{key} fora da faixa permitida.')
            if not number.is_integer() and key != 'rating_min' and range_field not in ('wage','wage_budget_weekly','release_fee','value','balance','transfer_budget_remaining','model_value','model_fee'):
                raise ValueError(f'{key} exige número inteiro.')
        if key == 'position' and not set(value.split(',')).issubset(POSITIONS):
            raise ValueError('Posição inválida.')
        if key in ('contract_before', 'contract_after'):
            date.fromisoformat(value)
        if key == 'league' and any(not re.fullmatch(r'(db|save):\d+', v) for v in value.split(',')):
            raise ValueError('Liga inválida.')
        if key in ('free', 'within_shortlist', 'no_contract', 'has_release') and value not in ('0', '1'):
            raise ValueError('Condição de clube inválida.')
        if key == 'release_kind' and not set(value.split(',')).issubset(RELEASE_KINDS):
            raise ValueError('Cláusula inválida.')
        if key == 'traits' and not re.fullmatch(r'\d+(,\d+)*', value):
            raise ValueError('Traits: use IDs separados por vírgula.')
        if key == 'squad_scope' and value not in ('first','all'):
            raise ValueError('Escopo de elenco inválido.')
        if key == 'squad' and value not in ('first','all','other'):
            raise ValueError('Equipe inválida.')
        if key == 'sort' and value not in ('name', 'age', 'club_name', 'ca', 'pa', 'attribute_sum', 'rating', 'reputation', 'nation_id', 'eu_national', 'goalkeeping_sum', 'ability_difference', 'rep_home', 'rep_current', 'rep_world', 'wage', 'value', 'release_fee', 'release_fee_domestic', 'release_fee_foreign', 'ca_mean','pa_mean','age_mean','player_count','ca_count','pa_count','age_count','team_slot','staff_area','staff_role','height_cm','balance','transfer_budget_remaining','wage_budget_weekly','stadium_seated_capacity','stadium_expansion_capacity','league_name','stadium_name','model_value','model_fee') and value not in {f'attr_{a}' for a in ATTRIBUTES}:
            raise ValueError('Ordenação inválida.')
        if key == 'direction' and value not in ('asc', 'desc'):
            raise ValueError('Direção inválida.')
        clean[key] = value
    if clean.get('age_min') and clean.get('age_max') and float(clean['age_min']) > float(clean['age_max']):
        raise ValueError('Idade mínima maior que a máxima.')
    for key in ATTRIBUTES:
        if f'attr_{key}' in clean and f'maxattr_{key}' in clean and float(clean[f'attr_{key}']) > float(clean[f'maxattr_{key}']):
            raise ValueError('Mínimo do atributo maior que o máximo.')
    for key in RANGES:
        if f'{key}_min' in clean and f'{key}_max' in clean and float(clean[f'{key}_min']) > float(clean[f'{key}_max']):
            raise ValueError(f'Mínimo de {key} maior que o máximo.')
    return {'id': secrets.token_hex(8), 'name': name.strip(), 'kind': kind, 'filters': clean}


class Presets:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        if data.get('version') != 1 or not isinstance(data.get('presets'), list):
            raise ValueError('Arquivo de filtros locais inválido; preserve-o para recuperação.')
        return data['presets']

    def write(self, presets):
        if len(presets) > 200:
            raise ValueError('Limite de 200 filtros salvos.')
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'version': 1, 'presets': presets}, ensure_ascii=False, indent=2))
        temporary.replace(self.path)

    def add(self, preset):
        clean = validate_filter(preset)
        rows = self.read()
        rows.append(clean)
        self.write(rows)
        return clean

    def import_file(self, document):
        if not isinstance(document, dict) or document.get('version') != 1 or not isinstance(document.get('presets'), list):
            raise ValueError('Use um arquivo de filtros FM Matt Scout, versão 1.')
        clean = [validate_filter(p) for p in document['presets']]
        current = self.read()
        keys = {(p['name'], p['kind'], json.dumps(p['filters'], sort_keys=True)) for p in current}
        added = [p for p in clean if (p['name'], p['kind'], json.dumps(p['filters'], sort_keys=True)) not in keys]
        self.write(current + added)
        return len(added)

    def remove(self, uid):
        self.write([p for p in self.read() if p['id'] != uid])
