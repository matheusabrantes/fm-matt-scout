"""Experimental manager/director seats, checked against the staff's own club contract."""
import re
import struct

ROLES = {'manager': 'Treinador principal', 'director_of_football': 'Diretor de futebol',
         'human_manager': 'Treinador (humano)', 'unknown': 'Cargo não identificado'}


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
