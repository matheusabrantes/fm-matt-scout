import sqlite3
import tempfile
import unittest
from pathlib import Path

from scout import Scout


class BatchShortlistTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.scout=Scout(Path(temp.name)/'scout.sqlite3')
        self.scout.meta={'date':'2025-12-30'};self.scout.career='carreira-a'
        self.scout.index={'players':{uid:{} for uid in (1,2,3)},'staff':{1:{}}}

    def test_add_and_remove_are_idempotent(self):
        self.assertEqual(self.scout.set_shortlist('players',[1,2,2],True),{'changed':2,'shortlist_count':2})
        self.assertEqual(self.scout.set_shortlist('players',[1,2],True),{'changed':0,'shortlist_count':2})
        self.assertEqual(self.scout.set_shortlist('players',[2,3],False),{'changed':1,'shortlist_count':1})
        self.assertEqual(self.scout.shortlisted('players'),{1})

    def test_invalid_batch_is_rejected_before_any_write(self):
        for kind,uids,add in [('clubs',[1],True),('players',[],True),('players',[1,99],True),
                              ('players',[True],True),('players',['1'],True),('players',[1],1),
                              ('players',{'1':1},True)]:
            with self.assertRaises(ValueError):self.scout.set_shortlist(kind,uids,add)
            self.assertEqual(self.scout.shortlisted('players'),set())
        self.scout.meta=None
        with self.assertRaises(ValueError):self.scout.set_shortlist('players',[1],True)

    def test_transaction_rolls_back_if_a_write_fails(self):
        with self.scout.db() as db:
            db.execute("CREATE TRIGGER reject_two BEFORE INSERT ON shortlist WHEN NEW.uid=2 BEGIN SELECT RAISE(ABORT,'falha de teste'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.scout.set_shortlist('players',[1,2],True)
        self.assertEqual(self.scout.shortlisted('players'),set())

    def test_careers_and_kinds_are_isolated(self):
        self.scout.set_shortlist('players',[1],True)
        self.scout.set_shortlist('staff',[1],True)
        self.scout.career='carreira-b'
        self.assertEqual(self.scout.shortlisted('players'),set())
        self.scout.set_shortlist('players',[2],True)
        self.scout.career='carreira-a'
        self.scout.set_shortlist('players',[1],False)
        self.assertEqual(self.scout.shortlisted('players'),set())
        self.assertEqual(self.scout.shortlisted('staff'),{1})
