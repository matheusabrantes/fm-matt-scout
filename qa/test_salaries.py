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
            self.assertEqual(store.view('career'),{'currency':'EUR','period':'month','rate':None})

    def test_reference_currency_and_career_remain_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            store=SalarySettings(Path(folder)/'salaries.json')
            settings=store.update('one',{'currency':'EUR','period':'month','amount':5200},{'wage':1000})
            self.assertAlmostEqual(settings['rate'],1.2)
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
