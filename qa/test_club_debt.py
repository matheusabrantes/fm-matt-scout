import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from club_debt import read_current_club_debts
from fmsave.readers.clubs import ClubRecordSpan


BUILD = '26.3.2+2329565'


def fm_date(year):
    return struct.pack('<HH', 1, year)


def loan(original=1200, flags=1):
    return (b'\x01' + struct.pack('<iiii', original, 20, 5, 0) + fm_date(2060)
            + bytes([5, 1, flags]) + fm_date(2024))


def tail():
    kit = bytearray(27)
    kit[0:2] = b'\x01\x01'
    handle = 'União'.encode()
    return (fm_date(1910) + b'\xff' * 4 + b'\x00\x00' + struct.pack('<I', len(handle))
            + handle + b'\x01' + kit)


def record(ordinal, rows=(), extras=0, header_entries=0):
    raw = bytearray(160)
    struct.pack_into('<I', raw, 0, ordinal)
    raw[4:6] = bytes([10, 12])
    raw[7] = header_entries
    for item in range(header_entries):
        struct.pack_into('<I', raw, 9 + 4 * item, 120 + item)
    raw[9 + 4 * header_entries] = 1
    dates = 19 + 4 * header_entries
    raw[dates:dates + 24] = fm_date(1900) * 6
    raw[dates + 24] = 1
    raw[dates + 25:dates + 49] = fm_date(1900) * 6
    raw += struct.pack('<I', len(rows)) + b''.join(rows)
    raw += struct.pack('<H', extras) + (b'\x02' + struct.pack('<iiH', 5, 7, 900)) * extras
    raw += tail() + b'\x7f' * 40
    return raw


class ClubDebtTests(unittest.TestCase):
    def fixture(self, rows=None):
        if rows is None:
            rows = [loan(), loan(2400, flags=0)]
        raw = bytearray(1024)
        spans = []
        for ordinal, uid, at in [(1, 318, 64), (2, 622, 192)]:
            struct.pack_into('<III', raw, at, ordinal - 1, uid - 1, uid - 1)
            spans.append(ClubRecordSpan(uid, at, at + 64, None))
        raw += struct.pack('<I', 4)
        offsets = []
        for ordinal in range(4):
            offsets.append(len(raw))
            raw += record(ordinal, rows if ordinal == 1 else (), extras=2 if ordinal == 1 else 0)
        return raw, spans, offsets

    def read(self, raw, spans, build=BUILD):
        return read_current_club_debts(bytes(raw), spans, build)

    def test_owner_comes_from_index_and_retains_original_units(self):
        raw, spans, _ = self.fixture()
        result = self.read(raw, spans)
        self.assertEqual(result[318]['loan_count'], 2)
        self.assertEqual(result[318]['loans'][0], {
            'original_amount': 1200, 'monthly_payment': 20, 'monthly_interest': 5,
            'conditional_amount': 0, 'start_date': '2024-01-01', 'end_date': '2060-01-01',
            'kind_raw': 5, 'flags_raw': [1, 1]})
        self.assertEqual(result[622], {'loans': [], 'loan_count': 0, 'loan_source': 'current'})
        self.assertNotIn('debt', result[318])

    def test_equal_terms_do_not_join_neighbor_clubs(self):
        raw, spans, offsets = self.fixture([loan()])
        old = record(2)
        replacement = record(2, [loan()])
        raw[offsets[2]:offsets[2] + len(old)] = replacement
        result = self.read(raw, spans)
        self.assertEqual(result[318]['loans'], result[622]['loans'])
        self.assertEqual(set(result), {318, 622})

    def test_missing_interest_preserves_the_other_observed_terms(self):
        raw, spans, offsets = self.fixture([loan()])
        struct.pack_into('<i', raw, offsets[1] + 164 + 9, -1)
        item = self.read(raw, spans)[318]['loans'][0]
        self.assertIsNone(item['monthly_interest'])
        self.assertEqual(item['original_amount'], 1200)

    def test_header_ids_are_counted_before_the_date_blocks(self):
        raw, spans, offsets = self.fixture()
        raw[offsets[2]:offsets[3]] = record(2, header_entries=10)
        self.assertEqual(self.read(raw, spans)[622]['loans'], [])

    def test_invalid_list_is_missing_not_empty_and_cannot_cross_next_club(self):
        raw, spans, offsets = self.fixture()
        struct.pack_into('<I', raw, offsets[1] + 160, 3)
        result = self.read(raw, spans)
        self.assertNotIn(318, result)
        self.assertEqual(result[622]['loans'], [])
        raw, spans, offsets = self.fixture()
        raw[offsets[1] + 164 + 22] = 7
        self.assertNotIn(318, self.read(raw, spans))

    def test_version_ownership_and_complete_header_count_are_required(self):
        raw, spans, offsets = self.fixture()
        self.assertEqual(self.read(raw, spans, '26.4.0'), {})
        self.assertEqual(self.read(raw[:offsets[-1] + 40], spans), {})
        broken = bytearray(raw)
        struct.pack_into('<I', broken, offsets[2], 77)
        self.assertEqual(self.read(broken, spans), {})
        struct.pack_into('<I', raw, spans[0].record_start + 8, 999)
        self.assertNotIn(318, self.read(raw, spans))

    def test_duplicate_owner_and_ambiguous_empty_envelope_are_rejected(self):
        raw, spans, offsets = self.fixture()
        self.assertNotIn(318, self.read(raw, [*spans, spans[0]]))
        second_tail = struct.pack('<IH', 0, 0) + tail()
        raw[offsets[3]:offsets[3]] = second_tail
        self.assertNotIn(622, self.read(raw, spans))


if __name__ == '__main__':
    unittest.main()
