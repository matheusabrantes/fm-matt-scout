import json
import unittest
from pathlib import Path

from presets import validate_filter
from scout import filter_rows
from value_model import estimate, enrich_estimates


class ValueModelTests(unittest.TestCase):
    def player(self, **changes):
        return dict(uid=1, name='Controle', age=25, ca=175, pa=190, rep_world=8750,
                    contract_state='contracted', contract_end='2027-06-30',
                    contract={'end_source':'contract','start':'2024-01-01'},
                    club_uid=1734, club_reputation=9098, value=131543072,
                    transfer_listed=False, wage=344735, **changes)

    def test_market_equation_and_purchase_do_not_overwrite_the_save(self):
        player = self.player()
        result = estimate(player, '2025-12-30', 7000, (2,26))
        self.assertEqual(player['value'], 131543072)
        self.assertEqual(result['model_fee_basis'], 'save')
        self.assertLess(result['model_value_low'], result['model_value'])
        self.assertGreater(result['model_fee_high'], result['model_fee'])
        self.assertEqual(result, estimate(player, '2025-12-30', 7000, (2,26)))

    def test_pinned_equation_and_fee_reference(self):
        result = estimate(self.player(), '2025-12-30', 7000, (2,26))
        self.assertEqual(result['model_regression_value'], 113900000)
        self.assertEqual(result['model_value'], 131543072)
        self.assertEqual(result['model_fee'], 123400000)
        self.assertEqual((result['model_fee_low'], result['model_fee_high']), (104890000,141910000))
        player=self.player();player.update(value=None,contract_end='2026-01-30')
        result=estimate(player,'2025-12-30')
        self.assertEqual(result['model_value'],26200000)
        player['contract_end']=None
        self.assertTrue(estimate(player,'2025-12-30')['model_assumptions'])

    def test_cor_and_madrid_ranges_do_not_replace_the_save_or_validate_purchase(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/value-model-controls.json').read_text())
        self.assertEqual(len(fixture['controls']),8)
        pure_inside=0
        for control in fixture['controls']:
            player=control['player'];result=estimate(player,fixture['game_date'])
            self.assertEqual(result['model_value'],player['value'])
            self.assertEqual(result['model_value_basis'],'save')
            self.assertLessEqual(control['fm_low'],result['model_value']*fixture['money_rate'])
            self.assertGreaterEqual(control['fm_high'],result['model_value']*fixture['money_rate'])
            pure=result['model_regression_value']*fixture['money_rate']
            pure_inside+=control['fm_low']<=pure<=control['fm_high']
        self.assertEqual(pure_inside,1, 'O controle não valida a regressão nas lacunas: só 1/8 dentro da faixa.')

    def test_unknown_inputs_and_expired_or_future_contracts_are_not_valued(self):
        for changes in [{'ca':None},{'age':None},{'pa':-10},{'rep_world':None},
                        {'contract_state':'unknown'},{'contract_end':'2020-01-01'},
                        {'contract':{'end_source':'contract','start':'2027-01-01'}},
                        {'contract_end':None,'contract':{'start':'2027-01-01'}}]:
            player = self.player();player.update(changes)
            self.assertIsNone(estimate(player, '2025-12-30')['model_value'])

    def test_zero_and_placeholder_use_model_only_in_separate_fields(self):
        for value in [0,None]:
            player=self.player();player['value']=value
            result=estimate(player,'2025-12-30')
            self.assertGreater(result['model_value'],0)
            self.assertEqual(result['model_fee_basis'],'model')
            self.assertEqual(player['value'],value)
        player=self.player();player['contract_state']='free'
        self.assertEqual(estimate(player,'2025-12-30')['model_fee'],0)

    def test_listing_buyer_and_wage_rank_have_expected_effects(self):
        player=self.player();player['transfer_listed']=True
        self.assertEqual(estimate(player,'2025-12-30',9500,(1,30))['model_fee'],player['value'])
        player['transfer_listed']=False
        low=estimate(player,'2025-12-30',5000,(30,30))['model_fee']
        high=estimate(player,'2025-12-30',9500,(1,30))['model_fee']
        self.assertGreater(high,low)

    def test_enrichment_uses_club_identity_and_repeated_wages(self):
        players=[]
        for uid in range(8):
            p=self.player();p.update(uid=uid,club_name='Mesmo nome',wage=100 if uid<2 else 10)
            players.append(p)
        for uid in range(8,16):
            p=self.player();p.update(uid=uid,club_uid=318,club_name='Mesmo nome',wage=1000)
            players.append(p)
        enrich_estimates(players,'2025-12-30',7000)
        self.assertEqual(players[0]['model_fee'],players[1]['model_fee'])
        self.assertGreater(players[0]['model_fee'],players[7]['model_fee'])
        self.assertEqual(players[0]['model_fee'],players[8]['model_fee'])

    def test_model_filters_are_separate_and_portable(self):
        player=self.player();player.update(estimate(player,'2025-12-30'))
        query={'kind':'players','model_fee_max':str(player['model_fee']),'sort':'model_value'}
        validate_filter({'name':'Modelo','kind':'players','filters':{k:v for k,v in query.items() if k!='kind'}})
        self.assertEqual(filter_rows([player],query),[player])


if __name__=='__main__':unittest.main()
