import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from club_locations import (read_current_club_links, stadium_reference_fields,
                            _localized_names, read_installed_names)
from fmsave.readers.clubs import ClubRecordSpan


BUILD = '26.3.2+2329565'


class ClubLocationTests(unittest.TestCase):
    def fixture(self):
        raw = bytearray(500)
        struct.pack_into('<III', raw, 20, 163, 317, 317)
        span = ClubRecordSpan(318, 20, 100, None)
        at = 218
        struct.pack_into('<I', raw, at - 18, 163)
        struct.pack_into('<III', raw, at - 4, 164, 317, 317)
        raw[at + 8] = 10
        raw[at + 10] = 7
        struct.pack_into('<H', raw, at + 11, 7000)
        struct.pack_into('<4I', raw, at + 13, 124, 125, 0xffffffff, 10972)
        return raw, span, at

    def test_current_division_is_distinct_from_previous_season(self):
        raw, span, _ = self.fixture()
        self.assertEqual(read_current_club_links(raw, [span], BUILD), {
            318: {'current_competition_id': 124, 'stadium_ordinal': 10972}})

    def test_wrong_owner_header_build_and_duplicate_are_unknown(self):
        raw, span, at = self.fixture()
        self.assertEqual(read_current_club_links(raw, [span], '26.4.0'), {})
        self.assertEqual(read_current_club_links(raw, [span, span], BUILD), {})
        for offset in [at - 18, at - 12, at + 4, at + 8, at + 9, span.record_start + 12]:
            wrong = bytearray(raw)
            wrong[offset] ^= 255
            self.assertEqual(read_current_club_links(wrong, [span], BUILD), {})
        wrong = bytearray(raw)
        struct.pack_into('<H', wrong, at + 11, 10001)
        self.assertEqual(read_current_club_links(wrong, [span], BUILD), {})
        raw[318:365] = raw[200:247]
        self.assertEqual(read_current_club_links(raw, [span], BUILD), {})
        self.assertEqual(read_current_club_links(raw[:at + 28], [span], BUILD), {})

    def test_missing_references_do_not_become_zero_ids(self):
        raw, span, at = self.fixture()
        struct.pack_into('<I', raw, at + 13, 0xffffffff)
        struct.pack_into('<I', raw, at + 25, 0xffffffff)
        self.assertEqual(read_current_club_links(raw, [span], BUILD)[318], {
            'current_competition_id': None, 'stadium_ordinal': None})

    def stadium(self, ordinal, uid, name=None):
        return SimpleNamespace(ordinal=ordinal, uid=uid, name=name,
                               all_seater=45000, expansion=60000)

    def test_stadium_database_id_comes_from_next_header_even_across_uid_gaps(self):
        rows = [self.stadium(1, 11), self.stadium(2, 40001), self.stadium(3, 50001, 'Novo nome')]
        result = stadium_reference_fields(SimpleNamespace(rows=rows),
            {11: 'Vizinho errado', 40000: 'Nome correto', 50000: 'Nome anterior'})
        self.assertEqual(result[2]['stadium_name'], 'Nome correto')
        self.assertEqual(result[2]['stadium_name_source'], 'installed_database')
        self.assertEqual(result[3]['stadium_name'], 'Nome anterior')
        self.assertEqual(result[4]['stadium_name'], 'Novo nome')
        self.assertEqual(result[4]['stadium_name_source'], 'save')
        self.assertEqual(result[2]['stadium_seated_capacity'], 45000)
        self.assertEqual(result[2]['stadium_expansion_capacity'], 60000)
        self.assertIsNone(stadium_reference_fields(SimpleNamespace(rows=rows[:1]), {})[2]['stadium_name'])

    def test_stadium_name_cannot_cross_a_missing_row(self):
        rows = [self.stadium(1, 11), self.stadium(3, 50001)]
        self.assertIsNone(stadium_reference_fields(SimpleNamespace(rows=rows),
                                                  {50000: 'Outro estádio'})[2]['stadium_name'])

    def test_localized_name_layouts_and_invalid_data(self):
        def text(label):
            encoded = label.encode()
            return struct.pack('<I', len(encoded)) + encoded
        header = b'\x03\x01tad.\x8d\x0e' + struct.pack('<I', 1)
        stadium = header + struct.pack('<I', 123) + text('Estádio União') + text('') + bytes(3)
        league = header + struct.pack('<I', 456) + b''.join(text(s) + b'\x00'
                                                          for s in ['Liga Atual', 'Liga', 'LA'])
        self.assertEqual(_localized_names(stadium, 2), {123: 'Estádio União'})
        self.assertEqual(_localized_names(league, 3), {456: 'Liga Atual'})
        for raw in [stadium[:-1], stadium + b'x', bytes(12), stadium[:16] + b'\xff' * 4]:
            with self.assertRaises(ValueError):
                _localized_names(raw, 2)
        self.assertEqual(read_installed_names('/missing/fm/lang_db.dat'), {})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'lang_db.dat'
            path.write_bytes(bytes(38))
            self.assertEqual(read_installed_names(path), {})


if __name__ == '__main__':
    unittest.main()
