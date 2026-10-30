"""Experimental professional attributes from the staff block documented by gilet."""

import re
import struct

from fmsave.readers.clubs import find_club_layouts
from staff_roles import ROLES, read_staff_roles, read_staff_contract_roles, read_staff_appointment_roles
from fmsave.readers.contracts import build_contract_decoder

from fmsave.readers.staff import find_staff_layouts, _header_reader, _header_values, _read_ability_block

# Offsets are relative to the validated ability block, before either attribute half.
SKILLS = {
    'authority': (18, 'Autoridade / disciplina'),
    'working_with_youngsters': (26, 'Trabalho com jovens'),
    'determination': (27, 'Determinação'),
    'goalkeeping': (41, 'Treino de goleiros'),
    'judging_player_ability': (42, 'Avaliação de capacidade'),
    'judging_player_potential': (43, 'Avaliação de potencial'),
    'people_management': (44, 'Gestão de pessoas'),
    'motivating': (45, 'Motivação'),
    'physiotherapy': (46, 'Fisioterapia'),
    'tactical_knowledge': (47, 'Conhecimento tático'),
    'attacking': (48, 'Treino ofensivo'),
    'defending': (49, 'Treino defensivo'),
    'fitness': (50, 'Treino físico'),
    'possession': (51, 'Treino de posse'),
    'technical': (52, 'Treino técnico'),
    'tactical': (53, 'Treino tático'),
    'gk_handling': (55, 'Goleiros: segurar bola (legado)'),
    'gk_distribution': (56, 'Goleiros: distribuição (legado)'),
    'judging_player_data': (58, 'Avaliação de dados'),
    'sports_science': (61, 'Ciência esportiva'),
    'negotiating': (63, 'Negociação'),
    'judging_staff_ability': (64, 'Avaliação de staff'),
    'set_pieces': (65, 'Bolas paradas'),
}
RAW_SKILLS = {'authority', 'working_with_youngsters'}
LEGACY_SKILLS = {'gk_handling', 'gk_distribution'}
SCORING_SKILLS = tuple(key for key in SKILLS if key not in LEGACY_SKILLS)


def skill_values(raw):
    return {key: (raw[index] if key in RAW_SKILLS else max(1, (raw[index] + 2) // 5))
            if index < len(raw) and 1 <= raw[index] <= (20 if key in RAW_SKILLS else 100) else None
            for key, (index, _) in SKILLS.items()}


def read_staff_skills(game_db, members, layout):
    targets = {row['uid']: row for row in members if not row.get('is_human_manager')}
    found, selectors, ambiguous = {}, {}, set()
    reader = _header_reader(layout)
    # Allocated headers can have unequal UID words; the reader validates their complete block.
    allocated_byte = re.escape(bytes([layout.allocated_uid_minimum >> 24]))
    pattern = rb'(?=(.{4})\1\x01|.{3}[' + allocated_byte + rb'-\xff].{4}\x01)'
    for match in re.finditer(pattern, game_db, re.DOTALL):
        uid = struct.unpack_from('<I', game_db, match.start())[0]
        member = targets.get(uid)
        if member is None:
            continue
        header = match.start() - layout.uid_offset
        if _header_values(game_db, header, reader, layout) != (uid, layout.staff_kind):
            continue
        block, slots_ok, _, further_ok = _read_ability_block(game_db, header, layout)
        if block is None or not (slots_ok and further_ok):
            continue
        ability = member.get('ability') or {}
        if (block.ability.current, block.ability.potential) != (ability.get('current'), ability.get('potential')):
            continue
        if member.get('preferences') != {name: getattr(block.preferences, name) for name, _ in layout.named_preference_slots}:
            continue
        count = game_db[header + layout.entry_count_offset]
        start = header + layout.ability_base_offset + layout.entry_bytes * count
        skills = skill_values(game_db[start:start + layout.block_40_offset + layout.block_40_count])
        if uid in found:
            ambiguous.add(uid)
        else:
            found[uid] = skills
            selectors[uid] = struct.unpack_from('<I', game_db, header)[0] + 1
    return ({uid: values for uid, values in found.items() if uid not in ambiguous},
            {uid: selector for uid, selector in selectors.items() if uid not in ambiguous})


def enrich_staff_skills(save, members, clubs):
    layouts = find_staff_layouts(save.info.section_schemas, save.info.build)
    layout = layouts.staff
    with save._context.section('game_db') as game_db:
        skills, selectors = read_staff_skills(game_db, members, layout)
        by_selector = {}
        for member in members:
            selector = selectors.get(member['uid'])
            if selector is not None:
                by_selector.setdefault(selector, []).append(member)
        club_layout = find_club_layouts(save.info.section_schemas.get('game_db'), save.info.build).records
        # shortcut: only the 26.3.2 seat format is demonstrated; extend after another build is checked.
        roles = read_staff_roles(game_db, clubs, save._context.own_club_record_spans(), by_selector,
                                 club_layout.long_name_offset) if save.info.build.startswith('26.3.2+') else {}
        appointments = {}
        if save.info.build.startswith('26.3.2+'):
            club_index = save._context.club_index()
            decoder = build_contract_decoder(layouts.contracts, club_index,
                                             save.info.game_date, save.info.file_name)
            appointments = read_staff_appointment_roles(game_db, by_selector, club_index.team_to_club, layout)
            roles = {**appointments, **read_staff_contract_roles(game_db, by_selector, decoder, layouts), **roles}
    for member in members:
        key = (member['uid'], member.get('club_uid'))
        role = roles.get(key)
        if role and not member.get('is_human_manager'):
            member['staff_role_key'] = role
            member['staff_role'] = ROLES[role]
        if key in appointments:
            member['has_club_appointment'] = True
            member['staff_role_source'] = 'club_appointment'
            member['contract_state'] = 'contracted'
        member['professional_attributes'] = skills.get(member['uid'], {})
        values = [member['professional_attributes'].get(key) for key in SCORING_SKILLS]
        member['attribute_sum'] = sum(values) if all(value is not None for value in values) else None
