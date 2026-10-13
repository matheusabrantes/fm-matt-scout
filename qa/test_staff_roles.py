import struct
import unittest
from types import SimpleNamespace
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from staff_roles import read_staff_roles


class StaffRoleTests(unittest.TestCase):
    def setUp(self):
        self.club = {'uid':101,'name':'São','short_name':'São'}
        self.member = {'uid':10,'club_uid':101,'has_contract':True}
        self.members = {500:[self.member]}
        self.manager = bytearray(37)
        struct.pack_into('<II',self.manager,4,100,100)
        self.manager[12:14]=b'\x0a\x00'
        self.manager[25:29]=b'\xff'*4
        struct.pack_into('<I',self.manager,33,500)

    def read(self,raw,members=None,spans=()):
        return read_staff_roles(raw,[self.club],spans,members if members is not None else self.members,39)

    def test_manager_requires_complete_seat_and_unique_contract_in_same_club(self):
        self.assertEqual(self.read(self.manager),{(10,101):'manager'})
        for size in range(37):self.assertEqual(self.read(self.manager[:size]),{})
        for changes in ({'club_uid':102},{'has_contract':False}):
            self.assertEqual(self.read(self.manager,{500:[{**self.member,**changes}]}),{})
        self.assertEqual(self.read(self.manager,{500:[self.member,self.member]}),{})
        for offset in (8,12,25,33):
            corrupt=self.manager.copy();corrupt[offset]=0
            self.assertEqual(self.read(corrupt),{})

    def director(self):
        body=39+8+len('São'.encode())*2
        raw=bytearray(body+14);raw[body]=1
        struct.pack_into('<I',raw,body+3,500)
        raw[body+8]=1;struct.pack_into('<I',raw,body+9,600);raw[body+13]=1
        return raw,SimpleNamespace(club_uid=101,record_start=0,record_end=len(raw)),body

    def test_director_uses_utf8_lengths_record_bounds_and_valid_board(self):
        raw,span,body=self.director()
        self.assertEqual(self.read(raw,spans=[span]),{(10,101):'director_of_football'})
        for size in range(body,len(raw)):
            self.assertEqual(self.read(raw[:size],spans=[SimpleNamespace(club_uid=101,record_start=0,record_end=size)]),{})
        for offset,value in ((body,0),(body+8,9),(body+12,255),(body+13,0)):
            corrupt=raw.copy();corrupt[offset]=value
            self.assertEqual(self.read(corrupt,spans=[span]),{})

    def test_conflicting_members_or_roles_are_not_assigned(self):
        second=self.manager.copy();struct.pack_into('<I',second,33,501)
        members={**self.members,501:[{**self.member,'uid':11}]}
        self.assertEqual(self.read(self.manager+second,members),{})
        raw,span,_=self.director()
        self.assertEqual(self.read(raw+self.manager,spans=[span]),{})
