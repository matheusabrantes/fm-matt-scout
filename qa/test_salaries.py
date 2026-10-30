import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from salaries import SalarySettings, PERIODS


class SalaryTests(unittest.TestCase):
    def test_euro_monthly_default_does_not_invent_an_exchange_rate(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            self.assertEqual(store.view('career'),{'currency':'EUR','period':'month','rate':None,'money_rate':None,'money_source':None})

    def test_reference_currency_and_career_remain_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            settings=store.update('one',{'currency':'EUR','period':'month','amount':5200},{'wage':1000})
            self.assertAlmostEqual(settings['rate'],1.2)
            self.assertAlmostEqual(settings['money_rate'],1.2)
            self.assertEqual(settings['money_source'],'salary')
            self.assertAlmostEqual(1000*PERIODS['month']*settings['rate'],5200)
            self.assertAlmostEqual(1000*PERIODS['year']*settings['rate'],62400)
            self.assertIsNone(store.view('two')['rate'])
            self.assertIsNone(store.update('one',{'currency':'BRL','period':'week'})['rate'])
            self.assertAlmostEqual(store.update('one',{'currency':'EUR','period':'week'})['rate'],1.2)
            self.assertAlmostEqual(SalarySettings(store.path).view('one')['rate'],1.2)

    def test_bad_reference_does_not_overwrite_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            store.update('one',{'currency':'EUR','period':'month','amount':5200},{'wage':1000})
            before=store.path.read_bytes()
            for amount in (-1,0,float('nan'),float('inf'),True,'5200'):
                with self.assertRaises(ValueError):store.update('one',{'currency':'USD','period':'year','amount':amount},{'wage':1000})
            with self.assertRaises(ValueError):store.update('one',{'currency':'EUR','period':'month','amount':5200},{'wage':0})
            self.assertEqual(store.path.read_bytes(),before)

    def test_release_reference_converts_money_without_changing_salary_or_period(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            reference={'wage':1000,'contract':{'clauses':[
                {'kind':'minimum_fee_release','value':864206784,'parameter':None},
                {'kind':'relegation_release','value':864206,'parameter':None}]}}
            store.update('one',{'currency':'EUR','period':'month','amount':5200},reference)
            settings=store.update('one',{'currency':'EUR','period':'month',
                'money_amount':1000000000,'release_kind':'minimum_fee_release'},reference)
            self.assertAlmostEqual(settings['money_rate']*864206784,1000000000)
            self.assertAlmostEqual(settings['money_rate']*864206,1000000,delta=2)
            self.assertAlmostEqual(settings['rate'],1.2)
            self.assertEqual(settings['money_source'],'clause')
            self.assertEqual(store.update('one',{'currency':'EUR','period':'year'})['money_rate'],settings['money_rate'])
            self.assertIsNone(store.view('two')['money_rate'])
            self.assertIsNone(store.update('one',{'currency':'USD','period':'month'})['money_rate'])
            self.assertEqual(SalarySettings(store.path).update('one',{'currency':'EUR','period':'month'})['money_rate'],settings['money_rate'])

    def test_bad_release_reference_preserves_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            store.update('one',{'currency':'EUR','period':'month','amount':5200},{'wage':1000})
            before=store.path.read_bytes()
            body={'currency':'EUR','period':'month','money_amount':1000000000,'release_kind':'minimum_fee_release'}
            for reference in [None,{}, {'contract':{'clauses':[{'kind':'minimum_fee_release','value':0}]}},
                              {'contract':{'clauses':[{'kind':'minimum_fee_release','value':100,'parameter':5}]}},
                              {'contract':{'clauses':[{'kind':'appearance_fee','value':100}]}}]:
                with self.assertRaises(ValueError):store.update('one',body,reference)
            reference={'contract':{'clauses':[{'kind':'minimum_fee_release','value':100}]}}
            for amount in [-1,0,True,float('nan'),float('inf'),'100']:
                with self.assertRaises(ValueError):store.update('one',{**body,'money_amount':amount},reference)
            self.assertEqual(store.path.read_bytes(),before)
