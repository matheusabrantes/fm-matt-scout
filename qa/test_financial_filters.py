import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from presets import validate_filter
from scout import filter_rows


class FinancialFilterTests(unittest.TestCase):
    def test_fractional_raw_bounds_accept_market_value_and_club_budgets(self):
        for kind, field in [('players', 'value'), ('clubs', 'transfer_budget_remaining')]:
            query = {field + '_max': '833333.333333'}
            saved = validate_filter({'name': 'Até €1 milhão', 'kind': kind, 'filters': query})
            rows = [{'uid': 1, 'name': 'A', field: 833333},
                    {'uid': 2, 'name': 'B', field: 833334}]
            self.assertEqual(saved['filters'], query)
            self.assertEqual([r['uid'] for r in filter_rows(rows, {'kind': kind, **saved['filters']})], [1])

    def test_negative_balance_keeps_fractional_interval_and_excludes_missing_data(self):
        query = {'balance_min': '-100.25', 'balance_max': '-50.25'}
        saved = validate_filter({'name': 'Saldo negativo', 'kind': 'clubs', 'filters': query})
        rows = [{'uid': 1, 'name': 'A', 'balance': -101},
                {'uid': 2, 'name': 'B', 'balance': -75},
                {'uid': 3, 'name': 'C', 'balance': 0},
                {'uid': 4, 'name': 'D', 'balance': None}]
        self.assertEqual(saved['filters'], query)
        self.assertEqual([r['uid'] for r in filter_rows(rows, {'kind': 'clubs', **saved['filters']})], [2])

    def test_money_fraction_support_keeps_other_range_constraints(self):
        for field, value in [('value_min', '-1'), ('transfer_budget_remaining_min', '-1'),
                             ('age_min', '18.5'), ('balance_max', 'nan')]:
            with self.assertRaises(ValueError):
                validate_filter({'name': 'Inválido', 'kind': 'players', 'filters': {field: value}})
