"""Experimental professional attributes from the staff block documented by gilet."""

import re
import struct

from fmsave.readers.staff import find_staff_layouts, _header_reader, _header_values, _read_ability_block

SKILLS = {
    'judging_player_ability': (2, 'Avaliação de capacidade'),
    'judging_player_potential': (3, 'Avaliação de potencial'),
    'people_management': (4, 'Gestão de pessoas'),
    'motivating': (5, 'Motivação'),
    'physiotherapy': (6, 'Fisioterapia'),
    'tactical_knowledge': (7, 'Conhecimento tático'),
    'attacking': (8, 'Treino ofensivo'),
    'defending': (9, 'Treino defensivo'),
    'fitness': (10, 'Treino físico'),
    'possession': (11, 'Treino de posse'),
    'technical': (12, 'Treino técnico'),
    'tactical': (13, 'Treino tático'),
    'gk_handling': (15, 'Goleiros: segurar bola'),
    'gk_distribution': (16, 'Goleiros: distribuição'),
    'judging_player_data': (18, 'Avaliação de dados'),
    'sports_science': (21, 'Ciência esportiva'),
    'negotiating': (23, 'Negociação'),
    'judging_staff_ability': (24, 'Avaliação de staff'),
    'set_pieces': (25, 'Bolas paradas'),
}


def skill_values(raw):
    return {key: max(1, (raw[index] + 2) // 5) if index < len(raw) and 1 <= raw[index] <= 100 else None
            for key, (index, _) in SKILLS.items()}


def read_staff_skills(game_db, members, layout):
    targets = {row['uid']: row for row in members if not row.get('is_human_manager')}
    found, ambiguous = {}, set()
    reader = _header_reader(layout)
    # shortcut: allocated unequal-UID headers stay absent; replace this adapter when fmsave publishes skills.
    for match in re.finditer(rb'(?=(.{4})\1\x01)', game_db, re.DOTALL):
        uid = struct.unpack('<I', match.group(1))[0]
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
        start = header + layout.ability_base_offset + layout.entry_bytes * count + layout.block_40_offset
        skills = skill_values(game_db[start:start + layout.block_40_count])
        if uid in found:
            ambiguous.add(uid)
        else:
            found[uid] = skills
    return {uid: values for uid, values in found.items() if uid not in ambiguous}


def enrich_staff_skills(save, members):
    layout = find_staff_layouts(save.info.section_schemas, save.info.build).staff
    with save._context.section('game_db') as game_db:
        skills = read_staff_skills(game_db, members, layout)
    for member in members:
        member['professional_attributes'] = skills.get(member['uid'], {})
        values = [member['professional_attributes'].get(key) for key in SKILLS]
        member['attribute_sum'] = sum(values) if all(value is not None for value in values) else None
