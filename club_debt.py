"""Owned loan terms from the current club block; no remaining-debt estimate."""
import calendar
import re
import struct
from datetime import date, timedelta


_TABLE_START = re.compile(rb'(?=(..[\x00-\x02]\x00\x00{4}[\x00-\x14]{2}..\x00))', re.DOTALL)
_FOUNDING_START = re.compile(rb'(?=(.{3}[\x00\x07\x08]\xff{4}))', re.DOTALL)
_U32 = struct.Struct('<I')
_U16 = struct.Struct('<H')


def _date_ok(raw, at):
    if at + 4 > len(raw):
        return False
    packed, year = struct.unpack_from('<HH', raw, at)
    return 1800 <= year <= 2200 and 1 <= (packed & 511) <= 365 + calendar.isleap(year)


def _date_text(raw, at):
    packed, year = struct.unpack_from('<HH', raw, at)
    return str(date(year, 1, 1) + timedelta(days=(packed & 511) - 1))


def _header_ok(raw, at, ordinal):
    if at + 19 > len(raw) or _U32.unpack_from(raw, at)[0] != ordinal:
        return False
    dates = at + 19 + 4 * raw[at + 7]
    return (dates + 49 <= len(raw) and raw[at + 4] <= 20 and raw[at + 5] <= 20
            and raw[at + 8] == 0 and raw[dates + 24] == 1
            and all(_date_ok(raw, p) for first in (dates, dates + 25)
                    for p in range(first, first + 24, 4)))


def _table_headers(raw, minimum_count):
    tables = []
    for match in _TABLE_START.finditer(raw):
        count = _U32.unpack_from(raw, match.start())[0]
        start = match.start() + 4
        if not minimum_count <= count <= min(200000, len(raw) // 100):
            continue
        if not _header_ok(raw, start, 0):
            continue
        headers = [start]
        for ordinal in range(1, count):
            marker = _U32.pack(ordinal)
            position, candidates = headers[-1] + 100, []
            # shortcut: larger records need another verified format, rather than a wider scan.
            limit = min(headers[-1] + 12000, len(raw))
            while (position := raw.find(marker, position, limit)) >= 0:
                if _header_ok(raw, position, ordinal):
                    candidates.append(position)
                position += 1
            if len(candidates) != 1:
                break
            headers.append(candidates[0])
        if len(headers) == count:
            tables.append(headers)
    return tables[0] if len(tables) == 1 else None


def _kit_envelopes(raw, start, end):
    for match in _FOUNDING_START.finditer(raw, start + 100, end - 34):
        at = match.start()
        year_zero = _U16.unpack_from(raw, at + 2)[0] == 0 and _U16.unpack_from(raw, at)[0] < 367
        if not (_date_ok(raw, at) or year_zero) or raw[at + 4:at + 8] != b'\xff' * 4:
            continue
        length = _U32.unpack_from(raw, at + 10)[0]
        if length > 128 or at + 14 + length >= end:
            continue
        kits = at + 14 + length
        count = raw[kits]
        if count > 128 or kits + 1 + count * 27 > end:
            continue
        try:
            if not all(char.isprintable() for char in bytes(raw[at + 14:kits]).decode('utf-8')):
                continue
        except UnicodeDecodeError:
            continue
        if all(raw[row] in (0, 1) and raw[row + 1] in (0, 1)
               and raw[row + 24] <= 50 and raw[row + 25] <= 20 and raw[row + 26] in (0, 1)
               for row in range(kits + 1, kits + 1 + count * 27, 27)):
            yield at


def _loan_row(raw, at):
    if (raw[at] != 1 or not _date_ok(raw, at + 17) or not _date_ok(raw, at + 24)
            or raw[at + 21] > 16 or raw[at + 22] != 1 or raw[at + 23] not in (0, 1)):
        return None
    original, payment, interest, conditional = struct.unpack_from('<iiii', raw, at + 1)
    if min(original, payment, conditional) < 0 or interest < -1:
        return None
    return {'original_amount': original, 'monthly_payment': payment,
            'monthly_interest': None if interest == -1 else interest, 'conditional_amount': conditional,
            'start_date': _date_text(raw, at + 24),
            'end_date': _date_text(raw, at + 17), 'kind_raw': raw[at + 21],
            'flags_raw': list(raw[at + 22:at + 24])}


def _loans_in_record(raw, start, end):
    matches = []
    for founding in _kit_envelopes(raw, start, end):
        for extras in range(20):
            tail = founding - 2 - 11 * extras
            if tail < start or _U16.unpack_from(raw, tail)[0] != extras:
                continue
            if any(raw[tail + 2 + 11 * item] != 2 for item in range(extras)):
                continue
            for count in range(min(100, (tail - start - 4) // 28) + 1):
                count_at = tail - 4 - 28 * count
                if _U32.unpack_from(raw, count_at)[0] != count:
                    continue
                rows = [_loan_row(raw, at) for at in range(count_at + 4, tail, 28)]
                if all(row is not None for row in rows):
                    matches.append(rows)
    return matches[0] if len(matches) == 1 else None


def read_current_club_debts(game_db, spans, build):
    """Return raw current loan lists by club UID. Missing and an empty list differ.

    Amounts retain the save's internal currency. Original amounts are not current
    balances. The last table object has no verified ending and is not decoded.
    """
    if build != '26.3.2+2329565':
        return {}
    owners, seen_uids, ambiguous = {}, set(), set()
    for span in spans:
        at = span.record_start
        if not 0 <= at < at + 13 <= span.record_end <= len(game_db):
            continue
        index, uid, uid_copy = struct.unpack_from('<III', game_db, at)
        if uid + 1 != span.club_uid or uid != uid_copy or game_db[at + 12] != 0:
            continue
        ordinal = index + 1
        if ordinal in owners or span.club_uid in seen_uids:
            ambiguous.add(ordinal)
            ambiguous.update(key for key, value in owners.items() if value == span.club_uid)
        owners[ordinal] = span.club_uid
        seen_uids.add(span.club_uid)
    owners = {key: uid for key, uid in owners.items() if key not in ambiguous}
    if not owners:
        return {}
    headers = _table_headers(game_db, max(owners) + 1)
    if headers is None:
        return {}
    found = {}
    for ordinal, uid in owners.items():
        if ordinal + 1 >= len(headers):
            continue
        loans = _loans_in_record(game_db, headers[ordinal], headers[ordinal + 1])
        if loans is not None:
            found[uid] = {'loans': loans, 'loan_count': len(loans), 'loan_source': 'current'}
    return found
