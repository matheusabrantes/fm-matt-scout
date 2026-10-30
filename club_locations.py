"""Current division and home-ground references from owned club status objects."""
import re
import struct
from pathlib import Path

from fmsave._container import decompress_frame, parse_directory
from fmsave import FmsaveError


_STATUS = re.compile(rb'\x00{10}(.{4})(.{4})\2\x0a', re.DOTALL)
_U32 = struct.Struct('<I')
_BUILD = '26.3.2+2329565'


def read_current_club_links(game_db, spans, build):
    if build != _BUILD:
        return {}
    owners, duplicates = {}, set()
    for span in spans:
        at = span.record_start
        if not 0 <= at < at + 13 <= span.record_end <= len(game_db):
            continue
        index, uid, uid_copy = struct.unpack_from('<III', game_db, at)
        if uid != uid_copy or uid + 1 != span.club_uid or game_db[at + 12] != 0:
            continue
        if uid in owners:
            duplicates.add(uid)
        owners[uid] = index
    found, repeated = {}, set()
    for match in _STATUS.finditer(game_db):
        at = match.start() + 14
        uid = _U32.unpack_from(game_db, at)[0]
        if uid not in owners or uid in duplicates or match.start() < 4 or at + 29 > len(game_db):
            continue
        if (_U32.unpack_from(game_db, match.start() - 4)[0] != owners[uid]
                or _U32.unpack_from(game_db, at - 4)[0] >= 200000
                or game_db[at + 9] != 0
                or not 1 <= struct.unpack_from('<H', game_db, at + 11)[0] <= 10000):
            continue
        league = _U32.unpack_from(game_db, at + 13)[0]
        stadium = _U32.unpack_from(game_db, at + 25)[0]
        if uid + 1 in found:
            repeated.add(uid + 1)
        found[uid + 1] = {
            'current_competition_id': league if 0 < league < 200000 else None,
            'stadium_ordinal': stadium if 1 < stadium < 200000 else None,
        }
    return {uid: fields for uid, fields in found.items() if uid not in repeated}


def stadium_reference_fields(stadium_index, names):
    """Resolve current ground references; the next header holds this ground's DB ID.

    fmsave's public UID is a synthetic header UID + 1. It differs from the
    database ID when the installed database has gaps between stadium IDs.
    """
    found = {}
    rows = stadium_index.rows
    for index, row in enumerate(rows):
        next_row = rows[index + 1] if index + 1 < len(rows) else None
        database_id = (next_row.uid - 1 if next_row is not None
                       and next_row.ordinal == row.ordinal + 1 else None)
        name = row.name or names.get(database_id)
        found[row.ordinal + 1] = {
            'stadium_name': name,
            'stadium_name_source': 'save' if row.name else 'installed_database' if name else None,
            'stadium_seated_capacity': row.all_seater,
            'stadium_expansion_capacity': row.expansion,
        }
    return found


def _localized_names(raw, strings):
    if len(raw) < 12 or raw[:6] != b'\x03\x01tad.':
        raise ValueError('Cabeçalho da base de nomes inválido')
    count = _U32.unpack_from(raw, 8)[0]
    if count > 100000:
        raise ValueError('Contagem da base de nomes inválida')
    names, cursor = {}, 12
    for _ in range(count):
        if cursor + 4 > len(raw):
            raise ValueError('Base de nomes truncada')
        uid = _U32.unpack_from(raw, cursor)[0]
        cursor += 4
        labels = []
        for _ in range(strings):
            if cursor + 4 > len(raw):
                raise ValueError('Nome truncado')
            size = _U32.unpack_from(raw, cursor)[0]
            cursor += 4
            if size > 4096 or cursor + size + 1 > len(raw):
                raise ValueError('Tamanho de nome inválido')
            label = raw[cursor:cursor + size].decode('utf-8')
            cursor += size
            if any(ord(char) < 32 or ord(char) == 127 for char in label):
                raise ValueError('Texto da base de nomes inválido')
            labels.append(label)
            if strings == 3:
                # Competition names have a grammatical byte after each string.
                cursor += 1
        if strings == 2:
            cursor += 3
        if uid in names or cursor > len(raw):
            raise ValueError('Identidade da base de nomes inválida')
        names[uid] = labels[0]
    if cursor != len(raw):
        raise ValueError('Fim da base de nomes não reconhecido')
    return names


def read_installed_names(path=None):
    """Read local FM names without copying or redistributing its database.

    Missing installations and unsupported localization layouts leave names empty.
    """
    if path is None:
        path = (Path.home() / 'Library/Application Support/Steam/steamapps/common/'
                'Football Manager 26/fm.app/Contents/PlugIns/game_plugin.bundle/'
                'Contents/Resources/shared/data/database/db/2600/2600_fm/lang_db.dat')
    try:
        with Path(path).open('rb') as source:
            size = source.seek(0, 2)
            source.seek(0)
            header = source.read(38)
            if header[:6] != b'\x03\x01tad.' or header[12:18] != b'\x02\x01fmf.':
                return {}
            trailer = 12 + 9 + struct.unpack_from('<Q', header, 21)[0]
            if not 38 <= trailer < size - 9 or size - trailer > 8 * 1024**2:
                return {}
            source.seek(trailer)
            if source.read(6) != b'\x02\x01fmf.':
                return {}
            source.seek(trailer + 9)
            directory = decompress_frame(source.read(), expected_size=None, cap=8 * 1024**2,
                                         what='base de nomes', file_name='lang_db.dat')
            _, entries = parse_directory(directory, 'lang_db.dat')
            result = {}
            for name, key, strings in [('19_21', 'stadiums', 2), ('19_25', 'competitions', 3)]:
                selected = [entry for entry in entries if entry.name == name and entry.extension == '.dat']
                if len(selected) != 1:
                    continue
                entry = selected[0]
                if (entry.compressed_size > 8 * 1024**2 or entry.decompressed_size > 8 * 1024**2
                        or entry.frame_offset < 26 or 12 + entry.frame_end > trailer):
                    continue
                source.seek(12 + entry.frame_offset)
                raw = decompress_frame(source.read(entry.compressed_size),
                    expected_size=entry.decompressed_size, cap=8 * 1024**2,
                    what=name, file_name='lang_db.dat')
                result[key] = _localized_names(raw, strings)
            return result
    except (OSError, ValueError, UnicodeError, struct.error, FmsaveError):
        return {}
