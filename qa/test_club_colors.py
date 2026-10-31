import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fmsave.readers.clubs import ClubRecordSpan
from club_colors import (_club_database_ids, _club_palettes, _read_installed_database,
                         read_current_club_colors)


BUILD = '26.3.2+2329565'


def text(value):
    encoded = value.encode()
    return struct.pack('<I', len(encoded)) + encoded


def header(count):
    return b'\x03\x01tad.' + struct.pack('<HI', 4000, count)


class ClubColorTests(unittest.TestCase):
    def fixture(self):
        raw = bytearray(200)
        struct.pack_into('<III', raw, 20, 45, 169, 169)
        struct.pack_into('<III', raw, 100, 46, 170, 170)
        return raw, ClubRecordSpan(170, 20, 100, None)

    def palette(self, version='2600'):
        return {'club_background':'#102030', 'club_foreground':'#FAFAFA',
                'club_colors_source':'installed_database_' + version}

    def test_owned_closing_id_does_not_use_next_accepted_club_or_name(self):
        raw, span = self.fixture()
        with patch('club_colors._read_installed_database', return_value={170:self.palette()}) as read:
            self.assertEqual(read_current_club_colors(raw, [span], BUILD), {170:self.palette()})
            self.assertEqual(read.call_args.args[1], {170})

    def test_wrong_owner_version_bounds_and_duplicates_have_no_palette(self):
        raw, span = self.fixture()
        with patch('club_colors._read_installed_database', return_value={170:self.palette()}):
            self.assertEqual(read_current_club_colors(raw, [span], '26.4.0'), {})
            self.assertEqual(read_current_club_colors(raw, [span], BUILD, 4001), {})
            self.assertEqual(read_current_club_colors(raw, [span, span], BUILD), {})
            self.assertEqual(read_current_club_colors(raw[:111], [span], BUILD), {})
            for offset in (20, 24, 28, 32, 100, 104, 108):
                wrong = bytearray(raw)
                wrong[offset] ^= 255
                self.assertEqual(read_current_club_colors(wrong, [span], BUILD), {})
            wrong_span = ClubRecordSpan(171, 20, 100, None)
            self.assertEqual(read_current_club_colors(raw, [span, wrong_span], BUILD), {170:self.palette()})
            struct.pack_into('<III', raw, 120, 98, 250, 250)
            struct.pack_into('<III', raw, 160, 99, 170, 170)
            other = ClubRecordSpan(251, 120, 160, None)
            self.assertEqual(read_current_club_colors(raw, [span, other], BUILD), {})

    def test_original_database_version_wins_and_other_base_only_fills_missing_ids(self):
        raw, span = self.fixture()
        def read(path, wanted, version):
            return {170:self.palette(version)} if version == '2600' else {}
        with patch('club_colors._read_installed_database', side_effect=read) as read:
            result = read_current_club_colors(raw, [span], BUILD, database_version='26.2.0+0')
            self.assertEqual([call.args[2] for call in read.call_args_list], ['2620','2600'])
            self.assertEqual(result[170]['club_colors_source'], 'installed_database_2600')
        with patch('club_colors._read_installed_database', return_value={170:self.palette('2620')}) as read:
            result = read_current_club_colors(raw, [span], BUILD, database_version='26.2.0+0')
            self.assertEqual(read.call_count, 1)
            self.assertEqual(result[170]['club_colors_source'], 'installed_database_2620')

    def core_table(self):
        first = bytes(27) + text('Clube A') + text('A') + bytes(3) + struct.pack('<III', 0, 170, 170)
        second = (b'\x0c' + bytes(26) + text('Clube B') + text('B') + bytes(3)
                  + bytes(4) + struct.pack('<III', 1, 900, 900))
        return header(2) + b'\x00' + first + second + b'\x00\x00\x00\x00\x01' + struct.pack('<I', 900)

    def extra_table(self):
        def row(ordinal, label, kits, colors):
            return (struct.pack('<IHIH', ordinal, 1900, 0xffffffff, 0)
                    + text(label) + bytes([kits]) + bytes(kits * 27) + bytes.fromhex(colors))
        return (header(2) + row(0, 'A', 2, 'ff102030fffafafa')
                + row(1, 'B', 0, 'ff406080ffffffff'))

    def test_full_tables_join_by_ordinal_and_preserve_raw_rgb(self):
        selected = _club_database_ids(self.core_table(), {170, 900})
        self.assertEqual(selected, {0:170, 1:900})
        self.assertEqual(_club_database_ids(self.core_table(), {900}), {1:900})
        self.assertEqual(_club_palettes(self.extra_table(), selected), {
            170:{'club_background':'#102030','club_foreground':'#FAFAFA'},
            900:{'club_background':'#406080','club_foreground':'#FFFFFF'}})
        missing = self.extra_table().replace(bytes.fromhex('ff102030'), bytes.fromhex('00102030'))
        self.assertNotIn(170, _club_palettes(missing, selected))

    def test_truncated_tables_foreign_schema_duplicate_ids_and_extra_data_are_rejected(self):
        core, extra = self.core_table(), self.extra_table()
        for raw in (core[:-1], core + b'x', bytes(12), core[:6] + b'\x00\x00' + core[8:]):
            with self.assertRaises((ValueError, struct.error)):
                _club_database_ids(raw, {170})
        duplicate = core.replace(struct.pack('<III', 1, 900, 900), struct.pack('<III', 1, 170, 170))
        with self.assertRaises(ValueError):
            _club_database_ids(duplicate, {170})
        for raw in (extra[:-1], extra + b'x', extra.replace(struct.pack('<IHIH', 1, 1900, 0xffffffff, 0),
                                                           struct.pack('<IHIH', 0, 1900, 0xffffffff, 0))):
            with self.assertRaises((ValueError, struct.error)):
                _club_palettes(raw, {0:170, 1:900})

    def test_missing_or_unrecognized_installation_is_optional(self):
        self.assertEqual(_read_installed_database(Path('/missing/client_db.dat'), {170}, '2600'), {})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'client_db.dat'
            path.write_bytes(bytes(38))
            self.assertEqual(_read_installed_database(path, {170}, '2600'), {})


if __name__ == '__main__':
    unittest.main()
