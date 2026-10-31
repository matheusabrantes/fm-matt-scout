import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scout import contract_fields, filter_rows
from presets import validate_filter


def person(uid, end=None, **changes):
    row = {'uid': uid, 'name': str(uid), 'team_id': 10, 'club_uid': 20,
           'contract': {'club_uid': 20, 'start': '2024-01-01', 'end': end,
                        'end_source': 'contract', 'wage': 100, 'kind_code': 1}}
    row.update(changes)
    return contract_fields(row)


class MarketFilterTests(unittest.TestCase):
    def test_empty_contract_object_does_not_hide_free_players(self):
        free = person(1, team_id=None, club_uid=None, contract={
            'player_uid': 1, 'club_uid': None, 'team_id': None, 'start': '2024-01-01',
            'end': '2027-01-01', 'end_source': 'player_record',
            'wage': None, 'kind_code': None, 'chain': []})
        unknown = person(2, team_id=None, club_uid=None, contract=None)
        contracted = person(3, '2026-06-30')
        self.assertEqual([p['uid'] for p in filter_rows([free, unknown, contracted], {'no_contract': '1'})], [1])

    def test_expiry_uses_save_date_calendar_months_and_current_contracts(self):
        rows = [person(1, '2026-06-30'), person(2, '2026-07-01'),
                person(3, '2025-12-29'), person(4, '2026-12-30'),
                person(5, '2026-12-31')]
        rows.append(person(6, '2026-05-01', contract={**rows[0]['contract'], 'end_source': 'player_record'}))
        query = {'availability': 'expiring_6', 'sort': 'name', 'direction': 'asc'}
        self.assertEqual([r['uid'] for r in filter_rows(rows, query, game_date='2025-12-30')], [1])
        query['availability'] = 'expiring_12'
        self.assertEqual([r['uid'] for r in filter_rows(rows, query, game_date='2025-12-30')], [1, 2, 4])
        self.assertEqual(filter_rows(rows, query), [])
        leap = person(1, contract={'club_uid': 20, 'wage': 100, 'start': '2023-01-01',
                                  'end': '2024-02-29', 'end_source': 'contract'})
        self.assertEqual([r['uid'] for r in filter_rows([leap], {'availability': 'expiring_6'}, game_date='2023-08-31')], [1])

    def test_conditional_clause_is_not_a_general_release_fee(self):
        row = person(1, contract={'clauses': [{'kind': 'relegation_release', 'value': 864206}]})
        self.assertIsNone(row['release_fee'])
        self.assertEqual(len(filter_rows([row], {'release_kind': 'relegation_release', 'release_fee_max': '900000'})), 1)

    def test_release_columns_keep_national_foreign_and_other_conditions_separate(self):
        row = person(1, contract={'clauses': [
            {'kind': 'minimum_fee_release', 'value': 900},
            {'kind': 'minimum_fee_release_domestic', 'value': 700},
            {'kind': 'minimum_fee_release_foreign', 'value': 800},
            {'kind': 'minimum_fee_release_domestic_higher_division', 'value': 100},
            {'kind': 'relegation_release', 'value': 50},
            {'kind': 'minimum_fee_release_foreign', 'value': 10, 'parameter': 5}]})
        missing = person(2)
        for column, amount in [('release_fee', 900), ('release_fee_domestic', 700),
                               ('release_fee_foreign', 800)]:
            validate_filter({'name': 'Cláusula', 'kind': 'players', 'filters': {'sort': column}})
            self.assertEqual(row[column], amount)
            self.assertIsNone(missing[column])
            self.assertEqual([r['uid'] for r in filter_rows([missing, row],
                             {'sort': column, 'direction': 'asc'})], [1, 2])

    def test_quick_filters_are_portable_and_validated(self):
        for value in ['free', 'expiring_6', 'expiring_12', 'transfer_listed', 'loan_listed']:
            validate_filter({'name': 'Oportunidades', 'kind': 'players', 'filters': {'availability': value}})
        for kind, value in [('players', 'bogus'), ('staff', 'free'), ('clubs', 'expiring_6')]:
            with self.assertRaises(ValueError):
                validate_filter({'name': 'Inválido', 'kind': kind, 'filters': {'availability': value}})

    def test_converted_release_limits_preserve_fractional_raw_units(self):
        query = {'release_fee_max': '833333.333333'}
        saved = validate_filter({'name': 'Até €1 milhão', 'kind': 'players', 'filters': query})
        rows = [person(1, contract={'clauses': [{'kind': 'minimum_fee_release', 'value': 833333}]}),
                person(2, contract={'clauses': [{'kind': 'minimum_fee_release', 'value': 833334}]})]
        self.assertEqual(saved['filters'], query)
        self.assertEqual([r['uid'] for r in filter_rows(rows, saved['filters'])], [1])

    def test_listing_filters_require_explicit_status(self):
        rows = [person(1, transfer_listed=True, loan_listed=False),
                person(2, transfer_listed=False, loan_listed=True), person(3)]
        for field, expected in [('transfer_listed', 1), ('loan_listed', 2)]:
            self.assertEqual([r['uid'] for r in filter_rows(rows, {'availability': field})], [expected])


if __name__ == '__main__':
    unittest.main()
