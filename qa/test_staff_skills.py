import struct
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from staff_skills import SKILLS, SCORING_SKILLS, skill_values, read_staff_skills
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
        raw = bytearray([100]*66)
        raw[18] = raw[26] = 20
        values = skill_values(raw)
        self.assertEqual(len(values), 23)
        self.assertEqual(sum(values.values()), 460)
        self.assertEqual(len(SCORING_SKILLS), 21)
        self.assertEqual(sum(values[key] for key in SCORING_SKILLS), 420)
        self.assertNotIn('gk_handling', SCORING_SKILLS)
        self.assertNotIn('gk_distribution', SCORING_SKILLS)
        self.assertEqual(skill_values(bytes([1]*66))['motivating'], 1)
        self.assertEqual(skill_values(bytes([73]*66))['motivating'], 15)
        self.assertIsNone(skill_values(b'')['motivating'])
        self.assertIsNone(skill_values(bytes([101]*66))['motivating'])
        skills, selectors = read_staff_skills(bytes(self.block), [self.member], self.layout)
        self.assertEqual(skills[123]['motivating'], 20)
        self.assertEqual(skills[123]['authority'], 10)
        self.assertEqual(skills[123]['working_with_youngsters'], 10)
        self.assertEqual(skills[123]['determination'], 2)
        self.assertEqual(skills[123]['goalkeeping'], 20)
        self.assertEqual(selectors, {123:457})

    def test_authority_youngsters_and_determination_use_separate_scales(self):
        raw = bytearray([50]*66)
        raw[18], raw[26], raw[27], raw[41] = 17, 11, 68, 40
        values = skill_values(raw)
        self.assertEqual(values['authority'], 17)
        self.assertEqual(values['working_with_youngsters'], 11)
        self.assertEqual(values['determination'], 14)
        self.assertEqual(values['goalkeeping'], 8)
        for offset, key in ((18, 'authority'), (26, 'working_with_youngsters')):
            damaged = raw.copy(); damaged[offset] = 21
            self.assertIsNone(skill_values(damaged)[key])
        for value in (0, 101):
            damaged = raw.copy(); damaged[27] = value
            self.assertIsNone(skill_values(damaged)['determination'])

    def test_rejects_mismatched_identity_ability_preferences_and_invalid_blocks(self):
        for offset, value in [(8,124),(12,9),(21,101),(34,0),(35,9),(61,0)]:
            block = self.block.copy();block[offset] = value
            self.assertEqual(read_staff_skills(bytes(block), [self.member], self.layout), ({}, {}))
        self.assertEqual(read_staff_skills(bytes(self.block[:86]), [self.member], self.layout), ({}, {}))
        self.assertEqual(read_staff_skills(bytes(self.block), [{**self.member,'is_human_manager':True}], self.layout), ({}, {}))

    def test_duplicate_matching_blocks_are_not_assigned_arbitrarily(self):
        self.assertEqual(read_staff_skills(bytes(self.block)*2, [self.member], self.layout), ({}, {}))

    def test_allocated_unequal_uid_headers_use_the_same_full_block_checks(self):
        uid = self.layout.allocated_uid_minimum + 123
        member = {**self.member, 'uid': uid}
        block = self.block.copy()
        struct.pack_into('<II', block, 4, uid, 917111893)
        skills, selectors = read_staff_skills(bytes(block), [member], self.layout)
        self.assertEqual(sum(skills[uid].values()), 422)
        self.assertEqual(selectors, {uid: 457})
        for offset, value in [(12, 9), (21, 101), (35, 9), (61, 0)]:
            damaged = block.copy(); damaged[offset] = value
            self.assertEqual(read_staff_skills(bytes(damaged), [member], self.layout), ({}, {}))
        for other in (0, 0xffffffff):
            damaged = block.copy(); struct.pack_into('<I', damaged, 8, other)
            self.assertEqual(read_staff_skills(bytes(damaged), [member], self.layout), ({}, {}))
        ordinary = block.copy(); struct.pack_into('<I', ordinary, 8, uid)
        self.assertEqual(read_staff_skills(bytes(ordinary + block), [member], self.layout), ({}, {}))


if __name__ == '__main__':unittest.main()
