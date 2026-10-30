"""Staff seats and current contract roles, with independent ownership checks."""
import re
import struct

from fmsave.readers.staff import (
    _discovery_pattern, _header_reader, _header_values, locate_contracted_header,
)

CONTRACT_ROLES = {
    2: ('coach', 'Preparador'),
    4: ('chairperson', 'Presidente da direção'),
    6: ('director', 'Diretor'),
    10: ('director_of_football', 'Diretor de futebol'),
    12: ('physiotherapist', 'Fisioterapeuta'),
    14: ('scout', 'Olheiro'),
    16: ('team_manager', 'Treinador'),
    20: ('assistant_manager', 'Auxiliar técnico'),
    22: ('set_piece_coach', 'Preparador de bolas paradas'),
    26: ('fitness_coach', 'Preparador físico'),
    34: ('goalkeeping_coach', 'Preparador de goleiros'),
    38: ('club_doctor', 'Médico do clube'),
    40: ('head_sports_science', 'Chefe de ciência esportiva'),
    44: ('chief_scout', 'Chefe de olheiros'),
    46: ('doctor', 'Médico'),
    48: ('sports_scientist', 'Cientista esportivo'),
    50: ('head_physiotherapist', 'Chefe de fisioterapia'),
    58: ('recruitment_analyst', 'Analista de recrutamento'),
    60: ('performance_analyst', 'Analista de desempenho'),
    62: ('chief_recruitment_analyst', 'Coordenador de análise de recrutamento'),
    64: ('head_youth_development', 'Diretor de formação'),
    66: ('owner', 'Proprietário'),
    70: ('president', 'Presidente'),
    86: ('loan_manager', 'Gestor de empréstimos'),
    88: ('technical_director', 'Diretor técnico'),
}
ROLES = {key: label for key, label in CONTRACT_ROLES.values()}
ROLES.update(manager='Treinador principal', human_manager='Treinador (humano)', unknown='Cargo não identificado')


def read_staff_contract_roles(game_db, member_by_selector, decoder, layouts):
    candidates = {}
    reader = _header_reader(layouts.staff)
    for hit in _discovery_pattern(layouts.staff, layouts.contracts, layouts.team_lists).finditer(game_db):
        offset = hit.start()
        if offset + 21 >= len(game_db):
            continue
        selector = struct.unpack_from('<I', game_db, offset + layouts.contracts.selector_offset)[0]
        members = member_by_selector.get(selector, ())
        if not members:
            continue
        header = locate_contracted_header(game_db, selector - 1, offset, layouts.staff)
        if header is None:
            continue
        uid, _ = _header_values(game_db, header, reader, layouts.staff)
        record = decoder.decode_chain_record(game_db, offset)
        if (not record[6] or record[4] is None or record[4] > decoder.clock
                or (record[5] is not None and record[5] < decoder.clock)):
            continue
        matches = [member for member in members
                   if member.get('has_contract') and member['uid'] == uid
                   and (member.get('club_uid'), member.get('team_id'), member.get('wage'),
                        member.get('contract_start'), member.get('contract_end'))
                   == (record[0], record[2], record[3],
                       record[4].isoformat() if record[4] is not None else None,
                       record[5].isoformat() if record[5] is not None else None)]
        if len(matches) == 1:
            # The job belongs to this contract; ability-block r4 does not identify the current job.
            candidates.setdefault((uid, record[0]), []).append(game_db[offset + 21])
    return {key: CONTRACT_ROLES[codes[0]][0] for key, codes in candidates.items()
            if len(codes) == 1 and codes[0] in CONTRACT_ROLES}


def read_staff_roles(game_db, clubs, spans, member_by_selector, long_name_offset):
    club_by_uid = {club['uid']: club for club in clubs}
    candidates = []

    def member_for(selector, club_uid):
        matches = [member for member in member_by_selector.get(selector, ())
                   if member.get('club_uid') == club_uid and member.get('has_contract')]
        return matches[0] if len(matches) == 1 else None

    for hit in re.finditer(rb'(?=(.{4})\1\x0a\x00)', game_db, re.DOTALL):
        entry = hit.start() - 4
        if entry < 0 or entry + 37 > len(game_db):
            continue
        raw_uid = struct.unpack('<I', hit.group(1))[0]
        club = club_by_uid.get(raw_uid + 1)
        if club is None or raw_uid in (0, 0xffffffff):
            continue
        if game_db[entry + 25:entry + 29] != b'\xff' * 4:
            continue
        selector = struct.unpack_from('<I', game_db, entry + 33)[0]
        if not 0 < selector < 3_000_000:
            continue
        member = member_for(selector, club['uid'])
        if member:
            candidates.append((member['uid'], club['uid'], 'manager'))

    for span in spans:
        club = club_by_uid.get(span.club_uid)
        if club is None:
            continue
        body = (span.record_start + long_name_offset + 8
                + len(club['name'].encode('utf-8')) + len(club['short_name'].encode('utf-8')))
        if body + 10 > span.record_end or game_db[body] != 1:
            continue
        selector = struct.unpack_from('<I', game_db, body + 3)[0]
        count = game_db[body + 8]
        if count > 8 or body + 10 + count * 4 > span.record_end:
            continue
        if game_db[body + 9 + count * 4] != 1:
            continue
        board = [struct.unpack_from('<I', game_db, body + 9 + i * 4)[0] for i in range(count)]
        if any(not 0 < value < 3_000_000 for value in board) or not 0 < selector < 3_000_000:
            continue
        member = member_for(selector, club['uid'])
        if member:
            candidates.append((member['uid'], club['uid'], 'director_of_football'))

    by_seat, by_member = {}, {}
    for uid, club_uid, role in candidates:
        by_seat.setdefault((club_uid, role), set()).add(uid)
        by_member.setdefault((uid, club_uid), set()).add(role)
    return {(uid, club_uid): next(iter(roles))
            for (uid, club_uid), roles in by_member.items()
            if len(roles) == 1 and len(by_seat[(club_uid, next(iter(roles)))]) == 1}
