import contextlib
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from server import read_layouts, serve


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
        self.assertEqual(migrated['players'], ['name','age','club_name','model_value','model_fee','ca','wage'])
        self.assertEqual(migrated['staff'], old['staff'])
        self.assertEqual(migrated['clubs'], old['clubs'])
        self.assertEqual(json.loads(self.path.read_text())['_version'], 1)
        before = self.path.read_bytes()
        self.assertEqual(read_layouts(self.path), migrated)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_old_value_and_minimal_layout_receive_both_columns(self):
        self.path.write_text(json.dumps({'players':['name','age']}))
        self.assertEqual(read_layouts(self.path)['players'], ['name','model_value','model_fee','age'])

    def test_explicit_choices_after_migration_stay_saved(self):
        self.path.write_text(json.dumps({'players':['name','value'], '_version':1}))
        self.assertEqual(read_layouts(self.path), {'players':['name','value']})

    def test_invalid_or_future_layout_is_not_rewritten(self):
        for data in ([], {'players':'bad'}, {'players':['age']}, {'_version':2}):
            before=json.dumps(data);self.path.write_text(before)
            with self.assertRaises(ValueError):read_layouts(self.path)
            self.assertEqual(self.path.read_text(),before)

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
            self.assertEqual(json.loads(self.path.read_text())['_version'],1)
            with self.assertRaises(urllib.error.HTTPError):request({'players':['not-a-column']})
            self.assertEqual(request(),{'players':['name','age']})
        finally:
            server.shutdown();server.server_close();thread.join()
