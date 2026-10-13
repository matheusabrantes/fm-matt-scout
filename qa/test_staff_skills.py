import struct
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from staff_skills import SKILLS, skill_values, read_staff_skills
from fmsave.readers.staff import find_staff_layouts


class StaffSkillsTests(unittest.TestCase):
    def setUp(self):
        self.layout = find_staff_layouts({}, '26.3.2+2329565').staff
        self.member = {'uid': 123, 'ability': {'current':100,'potential':150},
                       'preferences': {name:10 for name, _ in self.layout.named_preference_slots}}
        self.block = bytearray(100)
        struct.pack_into('<III', self.block, 0, 456, 123, 123)
        self.block[12] = 1
        struct.pack_into('<Hh', self.block, 21, 100, 150)
        self.block[34] = 12
        self.block[35:61] = bytes([10]*26)
        self.block[61:87] = bytes([100]*26)

    def test_scaled_professional_values_exclude_preferences_and_unknown_slots(self):
        values = skill_values(bytes([100]*26))
        self.assertEqual(len(values), 19)
        self.assertEqual(sum(values.values()), 380)
        self.assertEqual(skill_values(bytes([1]*26))['motivating'], 1)
        self.assertEqual(skill_values(bytes([73]*26))['motivating'], 15)
        self.assertIsNone(skill_values(b'')['motivating'])
        self.assertIsNone(skill_values(bytes([101]*26))['motivating'])
        self.assertEqual(read_staff_skills(bytes(self.block), [self.member], self.layout)[123], values)

    def test_rejects_mismatched_identity_ability_preferences_and_invalid_blocks(self):
        for offset, value in [(8,124),(12,9),(21,101),(34,0),(35,9),(61,0)]:
            block = self.block.copy();block[offset] = value
            self.assertEqual(read_staff_skills(bytes(block), [self.member], self.layout), {})
        self.assertEqual(read_staff_skills(bytes(self.block[:86]), [self.member], self.layout), {})
        self.assertEqual(read_staff_skills(bytes(self.block), [{**self.member,'is_human_manager':True}], self.layout), {})

    def test_duplicate_matching_blocks_are_not_assigned_arbitrarily(self):
        self.assertEqual(read_staff_skills(bytes(self.block)*2, [self.member], self.layout), {})


if __name__ == '__main__':unittest.main()
