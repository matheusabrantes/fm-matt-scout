import unittest

from contract_reader import contract_state, listing_status


def unregistered(**changes):
    contract = dict(club_uid=None, team_id=None, wage=None, kind_code=None,
                    end_source='none', start=None, end=None, clauses=[])
    contract.update(changes)
    return dict(club_uid=None, team_id=None, contract=contract)


class ContractStateTests(unittest.TestCase):
    def test_listing_controls_verified_in_game_are_kept_separate(self):
        row = dict(club_uid=318, team_id=256, contract=dict(
            club_uid=318, kind_code=1, wage=100, start='2025-01-01',
            end='2027-06-30', end_source='contract', unknown={}))
        for code, expected in [(0, (False, False)), (1, (True, False)), (2, (False, True))]:
            row['contract']['unknown']['e39'] = code
            self.assertEqual(listing_status(row, '26.3.2+2329565', '2025-12-30'), expected)
        for code in (None, True, -1, 3, 64, 65, 128):
            row['contract']['unknown']['e39'] = code
            self.assertEqual(listing_status(row, '26.3.2+2329565', '2025-12-30'), (None, None))
        row['contract']['unknown']['e39'] = 1
        for build, clock in [('26.4.0', '2025-12-30'), ('26.3.2+2329565', '2028-01-01'),
                             ('26.3.2+2329565', '2024-12-30')]:
            self.assertEqual(listing_status(row, build, clock), (None, None))

    def test_explicit_missing_registration_and_empty_current_terms_is_free(self):
        self.assertEqual(contract_state(unregistered()), 'free')

    def test_missing_contract_or_registration_is_unknown(self):
        for row in ({}, {'club_uid': None, 'contract': None},
                    {'club_uid': None, 'team_id': None, 'contract': {}},
                    {'club_uid': None, 'team_id': None, 'contract': {'end': None}}):
            with self.subTest(row=row):
                self.assertEqual(contract_state(row), 'unknown')

    def test_unresolved_registered_team_is_not_free(self):
        row = unregistered()
        row['team_id'] = 42
        self.assertEqual(contract_state(row), 'unknown')

    def test_unresolved_contract_owner_with_wage_is_not_free(self):
        self.assertEqual(contract_state(unregistered(wage=500)), 'unknown')

    def test_youth_contract_without_pay_is_still_a_contract(self):
        for wage in (0, None):
            row = unregistered(club_uid=7, team_id=10, wage=wage, kind_code=3)
            self.assertEqual(contract_state(row), 'contracted')

    def test_zero_club_id_is_a_resolved_club(self):
        self.assertEqual(contract_state(unregistered(club_uid=0, wage=0, kind_code=1)), 'contracted')

    def test_zero_pay_without_end_or_type_can_be_only_an_offer(self):
        self.assertEqual(contract_state(unregistered(club_uid=7, wage=0)), 'unknown')

    def test_future_chain_does_not_replace_current_state(self):
        future = [dict(club_uid=7, start='2030-01-01', end='2032-06-30', has_terms=True)]
        self.assertEqual(contract_state(unregistered(chain=future)), 'free')
        self.assertEqual(contract_state(unregistered(club_uid=8, wage=100,
                                                     kind_code=1, chain=future)), 'contracted')

    def test_fallback_dates_alone_do_not_establish_current_contract(self):
        row = unregistered(start='2025-10-03', end='2028-11-16', end_source='player_record')
        self.assertEqual(contract_state(row), 'free')
        del row['team_id']
        self.assertEqual(contract_state(row), 'unknown')

    def test_terms_without_resolved_club_and_contract_dates_fail_closed(self):
        for changes in ({'kind_code': 3}, {'event_count': 0}, {'squad_status_code': 13},
                        {'end_source': 'contract'}, {'clauses': [{'kind': 'appearance_fee'}]},
                        {'wage': -1}):
            with self.subTest(changes=changes):
                self.assertEqual(contract_state(unregistered(**changes)), 'unknown')


if __name__ == '__main__':
    unittest.main()
