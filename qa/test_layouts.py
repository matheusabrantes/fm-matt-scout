import contextlib
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from server import COLUMN_GROUPS, ordered_columns, read_layouts, serve


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'layouts.json'

    def test_fresh_install_uses_frontend_defaults_without_creating_a_layout(self):
        self.assertEqual(read_layouts(self.path), {})
        self.assertFalse(self.path.exists())

    def test_migrate_once_and_preserve_other_columns_and_lists(self):
        old = {'players':['name','age','club_name','ca','value','wage','model_value'],
               'staff':['name','staff_role'], 'clubs':['name','balance']}
        self.path.write_text(json.dumps(old))
        migrated = read_layouts(self.path)
        self.assertEqual(migrated['players'], ['name','age','club_name','ca','model_value','model_fee','wage'])
        self.assertEqual(migrated['staff'], old['staff'])
        self.assertEqual(migrated['clubs'], old['clubs'])
        self.assertEqual(json.loads(self.path.read_text())['_version'], 2)
        before = self.path.read_bytes()
        self.assertEqual(read_layouts(self.path), migrated)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_old_value_and_minimal_layout_receive_both_columns(self):
        self.path.write_text(json.dumps({'players':['name','age']}))
        self.assertEqual(read_layouts(self.path)['players'], ['name','age','model_value','model_fee'])

    def test_explicit_choices_after_migration_stay_saved(self):
        self.path.write_text(json.dumps({'players':['name','value'], '_version':1}))
        self.assertEqual(read_layouts(self.path), {'players':['name','value']})

    def test_invalid_or_future_layout_is_not_rewritten(self):
        for data in ([], {'players':'bad'}, {'players':['age']}, {'_version':3}):
            before=json.dumps(data);self.path.write_text(before)
            with self.assertRaises(ValueError):read_layouts(self.path)
            self.assertEqual(self.path.read_text(),before)

    def test_reorder_all_lists_without_changing_selection_or_restoring_removed_columns(self):
        old={'players':['release_fee','attr_passing','name','ca','club_name','age'],
             'staff':['attr_sports_science','wage','attribute_sum','name','staff_role','nation_id'],
             'clubs':['stadium_name','pa_mean','transfer_budget_remaining','league_name','name','nation_id'],
             '_version':1}
        self.path.write_text(json.dumps(old))
        result=read_layouts(self.path)
        self.assertEqual(result['players'],['name','age','club_name','ca','release_fee','attr_passing'])
        self.assertEqual(result['staff'],['name','nation_id','staff_role','attribute_sum','wage','attr_sports_science'])
        self.assertEqual(result['clubs'],['name','nation_id','league_name','pa_mean','transfer_budget_remaining','stadium_name'])
        for kind in ('players','staff','clubs'):
            self.assertCountEqual(result[kind],old[kind])
        before=self.path.read_bytes()
        self.assertEqual(read_layouts(self.path),result)
        self.assertEqual(self.path.read_bytes(),before)

    def test_groups_cover_every_staff_skill_without_duplicates_and_keep_unknown_columns(self):
        from scout import GROUPS
        for groups in COLUMN_GROUPS.values():
            columns=[key for keys in groups.values() for key in keys]
            self.assertEqual(len(columns),len(set(columns)))
        skills={key for keys in COLUMN_GROUPS['staff'].values() for key in keys if key.startswith('attr_')}
        expected={f'attr_{key}' for group in ('Profissionais','Personalidade') for key in GROUPS[group]}
        self.assertEqual(skills,expected)
        self.assertEqual(ordered_columns(['future_a','age','future_b','name'],'players'),
                         ['name','age','future_a','future_b'])

    def test_http_migration_and_later_user_choice_roundtrip(self):
        self.path.write_text(json.dumps({'players':['name','value']}))
        with contextlib.redirect_stdout(io.StringIO()):
            server,url=serve(storage=Path(self.temp.name)/'scout.sqlite3')
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            def request(body=None):
                req=urllib.request.Request(url+'api/layouts', data=json.dumps(body).encode() if body is not None else None,
                                           headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req) as response:return json.load(response)
            self.assertEqual(request(),{'players':['name','model_value','model_fee']})
            self.assertEqual(request({'players':['name','age']}),{'ok':True})
            self.assertEqual(request(),{'players':['name','age']})
            self.assertEqual(request({'players':['model_fee','name','ca']}),{'ok':True})
            self.assertEqual(request(),{'players':['name','ca','model_fee']})
            self.assertEqual(json.loads(self.path.read_text())['_version'],2)
            with self.assertRaises(urllib.error.HTTPError):request({'players':['not-a-column']})
            self.assertEqual(request(),{'players':['name','ca','model_fee']})
        finally:
            server.shutdown();server.server_close();thread.join()
