import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scout import SUM_FIELDS, GOALKEEPING, NATION_NAMES, NATION_REGIONS, EU_NATIONS, attribute_sum, enrich, filter_rows, club_squads, exclude_female_clubs, staff_fields, club_stadium_fields, club_league_fields
from presets import Presets, validate_filter


def player(uid=1, level=10, **changes):
    row = {'uid': uid, 'unique_id': uid, 'name': f'Jogador {uid}', 'age': 20,
           'attributes': {key: level for key in SUM_FIELDS}, 'positions': {'stc': 20},
           'ability': {'current': 100, 'potential': 150}, 'reputation': {'home': 1000, 'current': 2000, 'world': 500},
           'club_uid': 10, 'team_slot': 0, 'contract': None}
    row.update(changes)
    return enrich(row)


class ScoutTests(unittest.TestCase):
    def test_clubs_search_and_sort_use_short_names_without_overwriting_full_names(self):
        clubs=[{'uid':1,'name':'Z clube completo','short_name':'Alpha'},
               {'uid':2,'name':'A clube completo','short_name':'Zulu'},
               {'uid':3,'name':'Beta sem nome curto'}]
        query={'kind':'clubs','sort':'name','direction':'asc'}
        self.assertEqual([r['uid'] for r in filter_rows(clubs,query)],[1,3,2])
        self.assertEqual(filter_rows(clubs,{**query,'search':'alpha'}),[clubs[0]])
        self.assertEqual(filter_rows(clubs,{**query,'search':'Z clube completo'}),[clubs[0]])
        self.assertEqual(clubs[0]['name'],'Z clube completo')

    def test_staff_club_search_and_sort_follow_the_displayed_short_name(self):
        staff=[{'uid':1,'name':'Pessoa A','club_name':'Z clube completo','club_short_name':'Alpha'},
               {'uid':2,'name':'Pessoa B','club_name':'A clube completo','club_short_name':'Zulu'}]
        query={'kind':'staff','sort':'club_name','direction':'asc'}
        self.assertEqual([r['uid'] for r in filter_rows(staff,query)],[1,2])
        self.assertEqual(filter_rows(staff,{**query,'search':'alpha'}),[staff[0]])
        self.assertEqual(filter_rows(staff,{**query,'search':'Z clube completo'}),[staff[0]])

    def test_staff_medical_appointments_are_not_free_agents_without_decoded_terms(self):
        rows = [{'uid': 1, 'has_contract': False, 'has_club_appointment': True,
                 'contract_state': 'contracted'},
                {'uid': 2, 'has_contract': False}, {'uid': 3, 'has_contract': True}]
        self.assertEqual([r['uid'] for r in filter_rows(rows, {
            'kind': 'staff', 'no_contract': '1', 'sort': 'name'})], [2])

    def test_league_names_use_only_named_national_competitions_and_primary_team(self):
        clubs=[{'uid':1},{'uid':2},{'uid':3},{'uid':4}]
        competitions=[{'id':7,'database_id':11},{'id':8,'database_id':200},{'id':9,'database_id':22}]
        tables=[{'competition_id':7,'rows':[{'club_uid':1,'team_slot':0},{'club_uid':2,'team_slot':1},{'club_uid':4,'team_slot':0}]},
                {'competition_id':8,'rows':[{'club_uid':3,'team_slot':0}]},
                {'competition_id':9,'rows':[{'club_uid':4,'team_slot':0}]}]
        options=club_league_fields(clubs,competitions,tables,{11:'Premier League',22:'Bundesliga'})
        self.assertEqual(options,[{'key':'db:11','name':'Premier League'}])
        self.assertEqual(clubs[0]['league_name'],'Premier League')
        self.assertTrue(all(c['league_key'] is None for c in clubs[1:]))
        self.assertEqual(filter_rows(clubs,{'kind':'clubs','league':'db:11','sort':'league_name'}),[clubs[0]])

    def test_exact_staff_roles_can_be_combined_and_saved_without_using_areas(self):
        rows=[{'uid':1,'staff_role_key':'manager'},{'uid':2,'staff_role_key':'director_of_football'},{'uid':3,'staff_role_key':'unknown'}]
        self.assertEqual([r['uid'] for r in filter_rows(rows,{'kind':'staff','staff_role':'manager,director_of_football','sort':'name'})],[1,2])
        preset={'name':'Cargos','kind':'staff','filters':{'staff_role':'manager,director_of_football'}}
        validate_filter(preset)
        for changes in ({'kind':'players'},{'filters':{'staff_role':'bogus_role'}}):
            with self.assertRaises(ValueError):validate_filter({**preset,**changes})

    def test_current_club_league_overrides_old_table_without_treating_cups_as_leagues(self):
        clubs = [{'uid':1}, {'uid':2}]
        tables = [{'competition_id':7,'rows':[{'club_uid':1,'team_slot':0},{'club_uid':2,'team_slot':0}]}]
        club_league_fields(clubs, [{'id':7,'database_id':200}], tables,
                           {11:'Premier League',200:'Copa'}, {1:{'current_competition_id':9}},
                           {9:11}, {11:'Premier League'})
        self.assertEqual(clubs[0]['league_name'], 'Premier League')
        self.assertIsNone(clubs[1]['league_name'])

    def test_player_determination_keeps_player_source_when_staff_uses_same_key(self):
        rows = [player(1, attributes={'determination':18}), player(2, attributes={'determination':10})]
        self.assertEqual([r['uid'] for r in filter_rows(rows, {'attr_determination':'15'})], [1])
        staff = [{'uid':3,'professional_attributes':{'determination':14},'attributes':{'determination':1}}]
        self.assertEqual([r['uid'] for r in filter_rows(staff, {'kind':'staff','attr_determination':'13'})], [3])

    def test_stadium_home_link_is_not_ownership_and_ambiguous_links_are_absent(self):
        clubs = [{'uid': 1}, {'uid': 2}, {'uid': 3}]
        club_stadium_fields(clubs, [
            {'owner_club_uid': 2, 'home_club_uids': [1], 'all_seater_capacity': 49000, 'expansion_capacity': 70000},
            {'home_club_uids': [3], 'all_seater_capacity': 100},
            {'home_club_uids': [3], 'all_seater_capacity': 200}])
        self.assertEqual(clubs[0]['stadium_seated_capacity'], 49000)
        self.assertNotIn('stadium_seated_capacity', clubs[1])
        self.assertNotIn('stadium_seated_capacity', clubs[2])

    def test_height_and_professional_attribute_filter_sort_and_presets(self):
        rows = [player(1, height_cm=190), player(2, height_cm=180), player(3, height_cm=None)]
        self.assertEqual([r['uid'] for r in filter_rows(rows, {'height_cm_min':'185','sort':'height_cm'})], [1])
        staff = [{'uid':1,'professional_attributes':{'motivating':18}}, {'uid':2,'professional_attributes':{'motivating':10}}, {'uid':3}]
        self.assertEqual([r['uid'] for r in filter_rows(staff, {'kind':'staff','attr_motivating':'15','sort':'attr_motivating'})], [1])
        self.assertEqual([r['uid'] for r in filter_rows(staff, {'kind':'staff','sort':'attr_motivating','direction':'asc'})], [2,1,3])
        validate_filter({'name':'Staff','kind':'staff','filters':{'sum_min':'380','attr_motivating':'18','sort':'height_cm'}})
        with self.assertRaises(ValueError):validate_filter({'name':'Staff','kind':'staff','filters':{'sum_min':'421'}})

    def test_female_clubs_are_identified_by_database_id_not_name_or_empty_squad(self):
        clubs=[{'uid':1,'unique_id':2000099872,'name':'Chelsea'},
               {'uid':2,'unique_id':631,'name':'Chelsea'},
               {'uid':3,'unique_id':None,'name':'Chelsea'},
               {'uid':4,'unique_id':999999,'name':'Desconhecido'}]
        people=[player(1,club_uid=1),player(2,club_uid=2),player(3,club_uid=3),player(4,club_uid=None)]
        clubs,people,staff,count=exclude_female_clubs(clubs,people,[{'club_uid':1},{'club_uid':2}])
        self.assertEqual(count,1)
        self.assertEqual([c['uid'] for c in clubs],[2,3,4])
        self.assertEqual(clubs[0]['gender'],'male')
        self.assertIsNone(clubs[1]['gender'])
        self.assertEqual([p['uid'] for p in people],[2,3,4])
        self.assertEqual(staff,[{'club_uid':2}])

    def test_staff_areas_are_multi_select_without_inventing_job_titles(self):
        staff=[{'uid':i,'name':str(i),'list_indexes':indices,'unknown':{'r4':26}} for i,indices in enumerate([(0,),(1,),(2,),(0,2),()])]
        for member in staff:staff_fields(member)
        self.assertEqual([r['uid'] for r in filter_rows(staff,{'kind':'staff','staff_area':'medical,recruitment','sort':'staff_area'})],[2,3,0])
        self.assertTrue(all(r['staff_role']=='Cargo não identificado' for r in staff))
        self.assertTrue(all(r['attribute_sum'] is None for r in staff))
        manager=staff[0] | {'is_human_manager':True};staff_fields(manager)
        self.assertEqual(manager['staff_area_keys'],['manager'])
        self.assertEqual(manager['staff_role'],'Treinador (humano)')
        preset=validate_filter({'name':'Áreas','kind':'staff','filters':{'staff_area':'coaching,recruitment'}})
        self.assertEqual(preset['filters']['staff_area'],'coaching,recruitment')
        with self.assertRaises(ValueError):validate_filter({'name':'Inválido','kind':'staff','filters':{'staff_area':'scout'}})

    def test_nation_names_and_alphabetical_sort_without_numeric_fallback(self):
        self.assertEqual(NATION_NAMES[189], 'Brasil')
        self.assertEqual(NATION_NAMES[162], 'Portugal')
        self.assertNotIn(999, NATION_NAMES)
        rows = [player(1, nation_id=189, nation_name='Brasil'),
                player(2, nation_id=145, nation_name='Alemanha'),
                player(3, nation_id=999, nation_name=None)]
        self.assertEqual([r['uid'] for r in filter_rows(rows, {'sort':'nation_id','direction':'asc'})], [2,1,3])

    def test_sum_has_36_unique_fields_and_excludes_hidden_and_keeper(self):
        self.assertEqual(len(SUM_FIELDS), 36)
        self.assertEqual(len(set(SUM_FIELDS)), 36)
        p = player()
        p['attributes'].update({key: 20 for key in GOALKEEPING})
        p['attributes']['consistency'] = 20
        self.assertEqual(attribute_sum(p['attributes']), 360)

    def test_missing_or_invalid_attributes_never_become_zero(self):
        for value in (None, 0, 21, 10.0, True):
            attrs = {key: 10 for key in SUM_FIELDS}
            attrs['passing'] = value
            self.assertIsNone(attribute_sum(attrs))

    def test_720_is_maximum(self):
        self.assertEqual(player(level=20)['attribute_sum'], 720)

    def test_tied_ability_uses_sum(self):
        a, b = player(1, 10), player(2, 11)
        self.assertEqual([r['uid'] for r in filter_rows([a,b], {'sort':'ca'})], [2,1])

    def test_combined_filters_and_inclusive_attribute_bounds(self):
        a, b = player(1,10), player(2,11)
        a['attributes']['injury_proneness'] = 5
        b['attributes']['injury_proneness'] = 15
        q = {'club':'10','age_min':'20','age_max':'20','ca_min':'100','pa_max':'150',
             'attr_passing':'10','maxattr_passing':'10','maxattr_injury_proneness':'5'}
        self.assertEqual([r['uid'] for r in filter_rows([a,b],q)], [1])

    def test_unknown_attribute_fails_condition(self):
        p = player(); p['personality'] = {}
        self.assertEqual(filter_rows([p], {'attr_professionalism':'15'}), [])

    def test_accent_insensitive_search(self):
        self.assertEqual(len(filter_rows([player(name='João Ávila')], {'search':'joao avila'})), 1)

    def test_multiple_choices_are_or_within_each_field_and_and_across_fields(self):
        people=[player(1,club_uid=10,nation_id=7,positions={'dc':20}),player(2,club_uid=11,nation_id=8,positions={'dm':20}),player(3,club_uid=12,nation_id=7,positions={'dc':20}),player(4,club_uid=10,nation_id=9,positions={'mc':20})]
        q={'club':'10,11','nation':'7,8','position':'DC,DM'}
        self.assertEqual({r['uid'] for r in filter_rows(people,q)}, {1,2})
        valid=validate_filter({'name':'Vários','kind':'players','filters':q})
        self.assertEqual(valid['filters'],q)

    def test_multiple_leagues_and_release_kinds(self):
        p=player(league_key='db:10',competition_keys=['db:12'],contract={'clauses':[{'kind':'relegation_release','value':100}]})
        self.assertEqual(len(filter_rows([p],{'league':'db:10,db:11','release_kind':'relegation_release,non_promotion_release'})),1)
        self.assertEqual(filter_rows([p],{'league':'db:12'}),[])
        for filters in ({'club':'10,invalid'},{'nation':'1,,2'},{'position':'DC,BAD'},{'league':'db:10,BAD'},{'release_kind':'relegation_release,BAD'}):
            with self.assertRaises(ValueError):validate_filter({'name':'Inválido','kind':'players','filters':filters})

    def test_regions_use_nationality_and_club_separately_with_unknowns_excluded(self):
        self.assertEqual(NATION_REGIONS[189], 'south_america')
        self.assertEqual(NATION_REGIONS[162], 'europe')
        self.assertEqual(NATION_REGIONS[105], 'south_america')
        self.assertEqual(NATION_REGIONS[149], 'asia')
        self.assertEqual(set(NATION_REGIONS), set(NATION_NAMES))
        rows = [player(1,nation_id=189,club_region='europe'),
                player(2,nation_id=162,club_region='south_america'),
                player(3,nation_id=None,club_region=None)]
        query={'nation_region':'south_america,asia','based_region':'europe'}
        self.assertEqual([r['uid'] for r in filter_rows(rows,query)], [1])
        self.assertEqual(len(filter_rows(rows,{'based_region':'europe,south_america'})),2)
        clean=validate_filter({'name':'Regiões','kind':'staff','filters':query})
        self.assertEqual(clean['filters'],query)
        with self.assertRaises(ValueError):validate_filter({'name':'Inválido','kind':'players','filters':{'based_region':'europa'}})

    def test_all_citizenships_are_searched_for_nation_region_and_eu(self):
        dual=player(1,nation_id=189,second_nation_ids=[162,150,162],home_grown_nation_ids=[139])
        brazilian=player(2,nation_id=189,second_nation_ids=[],home_grown_nation_ids=[162])
        unknown=player(3,nation_id=189,second_nation_ids=[999])
        self.assertEqual(dual['nation_ids'],[189,162,150])
        self.assertEqual(dual['nation_name'],'Brasil, Portugal, Itália')
        for filters in ({'nation':'162'},{'nation':'150'},{'nation_region':'europe'},{'eu_national':'yes'}):
            self.assertEqual([p['uid'] for p in filter_rows([dual,brazilian,unknown],filters)],[1])
        self.assertEqual([p['uid'] for p in filter_rows([dual,brazilian,unknown],{'eu_national':'no'})],[2])
        self.assertIsNone(unknown['eu_national'])
        self.assertEqual(len(EU_NATIONS),27)
        for n in (139,159,167,175,160,172):self.assertNotIn(n,EU_NATIONS)
        self.assertIn(136,EU_NATIONS)

    def test_unknown_pa_sorts_last_in_both_directions(self):
        a, b = player(), player(2, ability={'current':100,'potential':None})
        for direction in ('asc','desc'):
            self.assertEqual(filter_rows([b,a], {'sort':'pa','direction':direction})[-1]['uid'], 2)

    def test_attribute_sort(self):
        self.assertEqual(filter_rows([player(1,10),player(2,15)], {'sort':'attr_passing'})[0]['uid'], 2)

    def test_first_team_and_all_club_averages(self):
        clubs = [{'uid':10}, {'uid':11}]
        people = [player(1,age=20), player(2,age=30,team_slot=1,ability={'current':80,'potential':None}), player(3,club_uid=None)]
        club_squads(clubs, people)
        first = clubs[0]['squad_metrics']['first']; all_players = clubs[0]['squad_metrics']['all']
        self.assertEqual(first['player_count'],1)
        self.assertEqual(all_players['ca_mean'],90)
        self.assertEqual(all_players['age_mean'],25)
        self.assertEqual(all_players['pa_mean'],150)
        self.assertEqual(all_players['pa_count'],1)
        self.assertIsNone(clubs[1]['squad_metrics']['all']['ca_mean'])

    def test_club_search_includes_youth_and_reserves_by_default(self):
        people = [player(1), player(2, team_slot=1, age=18), player(3, team_slot=2, age=17), player(4, club_uid=11)]
        self.assertEqual(len(filter_rows(people, {'club':'10'})),3)
        self.assertEqual(len(filter_rows(people, {'club':'10','squad':'first'})),1)
        self.assertEqual(len(filter_rows(people, {'club':'10','squad':'other'})),2)

    def test_release_filters_and_traits(self):
        p = player(contract={'kind_code':1,'squad_status_code':3,'clauses':[{'kind':'relegation_release','value':500}]},traits_code=[5,8])
        self.assertEqual(len(filter_rows([p],{'release_kind':'relegation_release','release_fee_max':'500','traits':'5,8'})),1)
        self.assertEqual(filter_rows([p],{'traits':'5,9'}),[])

    def test_presets_roundtrip_preserves_all_tactical_conditions(self):
        document = {'name':'Volante · 4-3-3','kind':'players','filters':{'position':'DM','club':'10','nation':'7','league':'db:10','nation_region':'south_america','based_region':'europe,asia','eu_national':'yes','age_min':'16','age_max':'23','attr_passing':'15','maxattr_injury_proneness':'7','sort':'attribute_sum'}}
        with tempfile.TemporaryDirectory() as d:
            source=Presets(Path(d)/'source.json'); target=Presets(Path(d)/'target.json')
            saved=source.add(document)
            count=target.import_file(json.loads(source.path.read_text()))
            self.assertEqual(count,1)
            self.assertEqual(target.read()[0]['filters'],saved['filters'])
            self.assertEqual(target.import_file(json.loads(source.path.read_text())),0)

    def test_invalid_import_is_atomic(self):
        with tempfile.TemporaryDirectory() as d:
            store=Presets(Path(d)/'filters.json')
            store.add({'name':'Antes','kind':'players','filters':{}})
            before=store.path.read_bytes()
            with self.assertRaises(ValueError):
                store.import_file({'version':1,'presets':[{'name':'Válido','kind':'players','filters':{}},{'name':'Inválido','kind':'players','filters':{'attr_passing':'21'}}]})
            self.assertEqual(store.path.read_bytes(),before)

    def test_invalid_presets_rejected(self):
        for values in ({'unknown':'1'}, {'age_min':'30','age_max':'20'}, {'attr_passing':'nan'}, {'attr_passing':'0'}, {'maxattr_passing':'5','attr_passing':'15'}, {'pa_max':'201'}, {'traits':'__import__'}, {'sort':'__dict__'}):
            with self.assertRaises(ValueError): validate_filter({'name':'Teste','kind':'players','filters':values})


if __name__ == '__main__':
    unittest.main()
