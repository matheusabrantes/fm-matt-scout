import unittest

from scout import enrich, filter_rows


class PlayerValueTests(unittest.TestCase):
    def player(self, state, value=None):
        return enrich({'uid': 1, 'name': 'Jogador', 'attributes': {},
                       'transfer_value': value, 'transfer_value_state': state,
                       'club_uid': 318, 'team_id': 38892,
                       'contract': {'club_uid': 318, 'kind_code': 1, 'wage': 72}})

    def test_zero_value_is_kept_and_does_not_mean_free_agent(self):
        row = self.player('zero')
        self.assertEqual(row['value'], 0)
        self.assertEqual(row['value_source'], 'save')
        self.assertEqual(row['value_status'], 'zero')
        self.assertEqual(row['contract_state'], 'contracted')
        self.assertEqual(filter_rows([row], {'availability': 'free'}), [])
        self.assertEqual(filter_rows([row], {'value_max': '1'}), [row])

    def test_missing_and_placeholder_values_remain_unknown(self):
        for state in ('placeholder', 'unset', 'other', None):
            with self.subTest(state=state):
                row = self.player(state)
                self.assertIsNone(row['value'])
                self.assertIsNone(row['value_source'])
                self.assertTrue(row['value_note'])
                self.assertEqual(filter_rows([row], {'value_max': '1'}), [])

    def test_positive_values_remain_from_the_save(self):
        row = self.player('ok', 131543072)
        self.assertEqual(row['value'], 131543072)
        self.assertEqual(row['value_source'], 'save')
        self.assertEqual(row['value_status'], 'ok')

    def test_invalid_or_contradictory_values_are_not_published(self):
        for state, value in [('zero', False), ('zero', 10), ('ok', True),
                             ('ok', -1), ('ok', 10.5), ('placeholder', 300000000),
                             ('unset', 1000)]:
            with self.subTest(state=state, value=value):
                self.assertIsNone(self.player(state, value)['value'])


if __name__ == '__main__':
    unittest.main()
