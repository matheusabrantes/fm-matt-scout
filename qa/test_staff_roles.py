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


class ContractRoleTests(unittest.TestCase):
    def setUp(self):
        from datetime import date
        from fmsave.readers.staff import find_staff_layouts
        self.layouts = find_staff_layouts({}, '26.3.2+2329565')
        self.member = {'uid':123,'club_uid':101,'has_contract':True,'team_id':77,'wage':500,
                       'contract_start':'2025-01-01','contract_end':'2026-06-30'}
        self.raw = bytearray(190)
        struct.pack_into('<III',self.raw,0,456,123,123);self.raw[12]=1
        struct.pack_into('<Hh',self.raw,21,100,150);self.raw[34]=12
        self.raw[35:61]=bytes([10]*26);self.raw[61:87]=bytes([100]*26)
        self.raw[150:154]=self.layouts.contracts.tag
        struct.pack_into('<II',self.raw,155,457,77)
        self.raw[171]=14
        self.record=(101,'Club',77,500,date(2025,1,1),date(2026,6,30),True)
        self.decoder=SimpleNamespace(clock=date(2025,6,1),
                                     decode_chain_record=lambda raw,offset:self.record)

    def read(self,raw=None,members=None):
        from staff_roles import read_staff_contract_roles
        return read_staff_contract_roles(bytes(self.raw if raw is None else raw),
            {457:[self.member] if members is None else members},self.decoder,self.layouts)

    def test_reads_current_contract_role_not_ability_role_byte(self):
        self.raw[25]=80
        self.assertEqual(self.read(),{(123,101):'scout'})
        self.raw[171]=26
        self.assertEqual(self.read(),{(123,101):'fitness_coach'})
        self.raw[171]=16
        self.assertEqual(self.read(),{(123,101):'team_manager'})
        self.raw[171]=58
        self.assertEqual(self.read(),{(123,101):'recruitment_analyst'})
        self.raw[171]=60
        self.assertEqual(self.read(),{(123,101):'performance_analyst'})
        self.raw[171]=22
        self.assertEqual(self.read(),{(123,101):'set_piece_coach'})
        self.raw[171]=62
        self.assertEqual(self.read(),{(123,101):'chief_recruitment_analyst'})

    def test_requires_unique_owned_matching_current_contract(self):
        for changes in ({'club_uid':102},{'uid':124},{'wage':501},{'team_id':78},
                        {'contract_start':'2025-01-02'},{'contract_end':'2026-06-29'},
                        {'has_contract':False}):
            self.assertEqual(self.read(members=[{**self.member,**changes}]),{})
        self.assertEqual(self.read(members=[self.member,self.member]),{})
        self.assertEqual(self.read(self.raw+self.raw[150:]),{})
        self.assertEqual(self.read(self.raw[:171]),{})
        self.raw[171]=255
        self.assertEqual(self.read(),{})
        self.raw[171]=14
        self.record=(*self.record[:6],False)
        self.assertEqual(self.read(),{})

    def test_future_or_expired_contract_does_not_supply_current_job(self):
        from datetime import date
        for clock in (date(2024,12,31),date(2026,7,1)):
            self.decoder.clock=clock
            self.assertEqual(self.read(),{})


class AppointmentRoleTests(unittest.TestCase):
    def setUp(self):
        from fmsave.readers.staff import find_staff_layouts
        self.layout = find_staff_layouts({}, '26.3.2+2329565').staff
        self.member = {'uid':123,'club_uid':101,'has_contract':False,
                       'in_club_lists':True,'list_indexes':[0],'unknown':{'r4':6}}
        self.raw = bytearray(205)
        struct.pack_into('<III',self.raw,0,456,123,123);self.raw[12]=1
        struct.pack_into('<Hh',self.raw,21,100,150);self.raw[34]=12
        self.raw[35:61]=bytes([10]*26);self.raw[61:87]=bytes([100]*26)
        self.offset = 164
        self.raw[172:174]=b'\x0a\x00';self.raw[174:178]=b'\xff'*4
        self.raw[178:180]=b'\x05\x05'
        struct.pack_into('<III',self.raw,180,457,77,0)
        struct.pack_into('<I',self.raw,192,500)
        self.raw[196]=46;self.raw[199:203]=b'\xff'*4
        self.team_to_club={77:(101,0)}

    def read(self,raw=None,member=None):
        from staff_roles import read_staff_appointment_roles
        return read_staff_appointment_roles(bytes(self.raw if raw is None else raw),
            {457:[self.member if member is None else member]},self.team_to_club,self.layout)

    def test_reads_owned_medical_job_without_using_r4_or_inventing_terms(self):
        self.assertEqual(self.read(),{(123,101):'doctor'})
        self.raw[172]=6
        self.assertEqual(self.read(),{(123,101):'doctor'})
        self.raw[196]=38
        self.assertEqual(self.read(),{(123,101):'club_doctor'})
        self.raw[196]=255
        self.assertEqual(self.read(),{})

    def test_requires_current_listing_owned_header_team_envelope_and_unique_record(self):
        for changes in ({'club_uid':102},{'uid':124},{'has_contract':True},
                        {'in_club_lists':False},{'list_indexes':[1]}):
            self.assertEqual(self.read(member={**self.member,**changes}),{})
        for offset in (8,12,172,178,180,184,198,199):
            damaged=self.raw.copy();damaged[offset]=255 if offset!=199 else 0
            self.assertEqual(self.read(damaged),{})
        self.assertEqual(self.read(self.raw[:202]),{})
        self.assertEqual(self.read(self.raw*2),{})

    def test_appointment_confirms_employment_without_inventing_contract_terms(self):
        from contextlib import nullcontext
        from datetime import date
        from staff_skills import enrich_staff_skills
        member = {**self.member, 'ability':{'current':100,'potential':150},
                  'preferences':{name:10 for name,_ in self.layout.named_preference_slots},
                  'wage':None,'contract_start':None,'contract_end':None,
                  'contract_state':'unknown','has_contract_data':False}
        index = SimpleNamespace(team_to_club=self.team_to_club, affiliate_team_to_club={},
                                club_by_uid={101:SimpleNamespace(name='Club')})
        save = SimpleNamespace(
            info=SimpleNamespace(section_schemas={},build='26.3.2+2329565',
                                 game_date=date(2025,12,30),file_name='COR.fm'),
            _context=SimpleNamespace(section=lambda _:nullcontext(bytes(self.raw)),
                                     club_index=lambda:index,own_club_record_spans=lambda:[]))
        enrich_staff_skills(save,[member],[])
        self.assertEqual(member['staff_role_key'],'doctor')
        self.assertTrue(member['has_club_appointment'])
        self.assertEqual(member['contract_state'],'contracted')
        self.assertFalse(member['has_contract'])
        self.assertFalse(member['has_contract_data'])
        self.assertIsNone(member['wage'])
        self.assertIsNone(member['contract_start'])
        self.assertIsNone(member['contract_end'])
        self.assertEqual(member['attribute_sum'],382)
