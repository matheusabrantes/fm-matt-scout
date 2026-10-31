"""Installed club palettes, joined through the save's owned database identifiers."""

import struct
from collections import Counter
from pathlib import Path

from fmsave import FmsaveError
from fmsave._container import decompress_frame, parse_directory


_BUILD = '26.3.2+2329565'
_SCHEMA = 4000
_LIMIT = 64 * 1024**2
_DATABASE_ROOT = (Path.home() / 'Library/Application Support/Steam/steamapps/common/'
                  'Football Manager 26/fm.app/Contents/PlugIns/game_plugin.bundle/'
                  'Contents/Resources/shared/data/database/db')


def _table_count(raw):
    if (len(raw) < 12 or raw[:6] != b'\x03\x01tad.'
            or struct.unpack_from('<H', raw, 6)[0] != _SCHEMA):
        raise ValueError('Unsupported club table header')
    count = struct.unpack_from('<I', raw, 8)[0]
    if not 0 < count <= 200000:
        raise ValueError('Invalid club table count')
    return count


def _text_end(raw, cursor):
    size = struct.unpack_from('<I', raw, cursor)[0]
    end = cursor + 4 + size
    if size > 4096 or end > len(raw):
        raise ValueError('Invalid club text extent')
    text = raw[cursor + 4:end].decode('utf-8')
    if any(ord(char) < 32 or ord(char) == 127 for char in text):
        raise ValueError('Invalid club text')
    return end


def _club_database_ids(raw, wanted):
    count = _table_count(raw)
    if len(raw) < 13 or raw[12] != 0:
        raise ValueError('Invalid club table prefix')
    cursor, selected, seen = 13, {}, set()
    for expected in range(count):
        if cursor + 27 > len(raw):
            raise ValueError('Truncated club prefix')
        prefix_flags = raw[cursor]
        cursor += 27
        cursor = _text_end(raw, cursor)
        cursor = _text_end(raw, cursor)
        if cursor + 3 > len(raw):
            raise ValueError('Truncated club flags')
        cursor += 3
        if prefix_flags == 0x0c:
            cursor += 4
        ordinal, database_id, copy = struct.unpack_from('<III', raw, cursor)
        cursor += 12
        if ordinal != expected or database_id != copy or database_id in seen:
            raise ValueError('Invalid club table identity')
        seen.add(database_id)
        if database_id in wanted:
            selected[ordinal] = database_id
    tail = raw[cursor:]
    if len(tail) != 9 or tail[:5] != b'\x00\x00\x00\x00\x01':
        raise ValueError('Unsupported club table ending')
    return selected


def _club_palettes(raw, selected):
    cursor, result = 12, {}
    for expected in range(_table_count(raw)):
        ordinal, year, missing, flags = struct.unpack_from('<IHIH', raw, cursor)
        if ordinal != expected or missing != 0xffffffff:
            raise ValueError('Invalid club palette identity')
        cursor = _text_end(raw, cursor + 12)
        if cursor >= len(raw):
            raise ValueError('Truncated club kits')
        cursor += 1 + raw[cursor] * 27
        if cursor + 8 > len(raw):
            raise ValueError('Truncated club palette')
        background, foreground = raw[cursor:cursor + 4], raw[cursor + 4:cursor + 8]
        cursor += 8
        if ordinal in selected and background[0] == foreground[0] == 255:
            result[selected[ordinal]] = {
                'club_background': '#' + background[1:].hex().upper(),
                'club_foreground': '#' + foreground[1:].hex().upper(),
            }
    if cursor != len(raw):
        raise ValueError('Unsupported club palette ending')
    return result


def _read_installed_database(path, wanted, version):
    try:
        with path.open('rb') as source:
            before = path.stat()
            header = source.read(38)
            if header[:6] != b'\x03\x01tad.' or header[12:18] != b'\x02\x01fmf.':
                return {}
            trailer = 12 + 9 + struct.unpack_from('<Q', header, 21)[0]
            if not 38 <= trailer < before.st_size - 9 or before.st_size - trailer > 8 * 1024**2:
                return {}
            source.seek(trailer)
            if source.read(6) != b'\x02\x01fmf.':
                return {}
            source.seek(trailer + 9)
            directory = decompress_frame(source.read(), expected_size=None, cap=8 * 1024**2,
                                         what='club directory', file_name=path.name)
            _, entries = parse_directory(directory, path.name)
            tables = {}
            for name in ('table_3', 'table_extra_3'):
                matching = [entry for entry in entries if entry.name == name and entry.extension == '.dat']
                if len(matching) != 1:
                    return {}
                entry = matching[0]
                if (entry.compressed_size > _LIMIT or entry.decompressed_size > _LIMIT
                        or sum(len(table) for table in tables.values()) + entry.decompressed_size > _LIMIT
                        or entry.frame_offset < 26 or 12 + entry.frame_end > trailer):
                    return {}
                source.seek(12 + entry.frame_offset)
                tables[name] = decompress_frame(source.read(entry.compressed_size),
                    expected_size=entry.decompressed_size, cap=_LIMIT, what=name, file_name=path.name)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                return {}
        if _table_count(tables['table_3']) != _table_count(tables['table_extra_3']):
            return {}
        selected = _club_database_ids(tables['table_3'], wanted)
        result = _club_palettes(tables['table_extra_3'], selected)
        for fields in result.values():
            fields['club_colors_source'] = f'installed_database_{version}'
        return result
    except (OSError, ValueError, UnicodeError, struct.error, FmsaveError):
        return {}


def read_current_club_colors(game_db, spans, build, schema=None, database_version=None):
    if build != _BUILD or schema not in (None, _SCHEMA):
        return {}
    owners, claimed = [], Counter(span.club_uid for span in spans)
    for span in spans:
        start, end = span.record_start, span.record_end
        if not 0 <= start < start + 13 <= end <= len(game_db) - 12:
            continue
        ordinal, uid, copy = struct.unpack_from('<III', game_db, start)
        closing, database_id, database_copy = struct.unpack_from('<III', game_db, end)
        if (uid != copy or uid + 1 != span.club_uid or game_db[start + 12] != 0
                or closing != ordinal + 1 or database_id != database_copy or database_id == 0xffffffff
                or claimed[span.club_uid] != 1):
            continue
        owners.append((span.club_uid, database_id))
    duplicates = Counter(database_id for _, database_id in owners)
    owners = [(uid, database_id) for uid, database_id in owners if duplicates[database_id] == 1]
    wanted, palettes = {database_id for _, database_id in owners}, {}
    versions = ('2620', '2600') if str(database_version).split('+')[0] == '26.2.0' else ('2600', '2620')
    for version in versions:
        missing = wanted - palettes.keys()
        if not missing:
            break
        path = _DATABASE_ROOT / version / f'{version}_fm' / 'client_db.dat'
        palettes.update(_read_installed_database(path, missing, version))
    return {uid: palettes[database_id] for uid, database_id in owners if database_id in palettes}
