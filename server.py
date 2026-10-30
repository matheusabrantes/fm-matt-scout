import argparse
import csv
import io
import json
import mimetypes
import secrets
import threading
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from scout import GROUPS, ROLES, NATION_NAMES, REGIONS, STAFF_AREAS, STAFF_ROLES, Scout, filter_rows, column_value
from staff_skills import SCORING_SKILLS
from presets import Presets, validate_filter
from salaries import SalarySettings
from fmsave.models.players import Trait

ROOT = Path(__file__).parent
SAVE_DIR = Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 26/games'



def read_layouts(path):
    if not path.exists():
        return {}
    layout = json.loads(path.read_text())
    if not isinstance(layout, dict):
        raise ValueError('Layout inválido.')
    version = layout.pop('_version', 0)
    if version not in (0, 1):
        raise ValueError('Versão de layout não suportada.')
    if version == 0:
        if 'players' in layout:
            if not isinstance(layout['players'], list):
                raise ValueError('Layout de jogadores inválido.')
            columns = [c for c in layout['players'] if c not in ('value', 'model_value', 'model_fee')]
            anchor = 'club_name' if 'club_name' in columns else 'name'
            index = columns.index(anchor) + 1
            columns[index:index] = ['model_value', 'model_fee']
            layout['players'] = columns
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps({**layout, '_version': 1}))
        temporary.replace(path)
    return layout


def serve(port=0, storage=None):
    token = secrets.token_urlsafe(32)
    scout = Scout(storage or Path.home() / 'Library/Application Support/FM Matt Scout/scout.sqlite3')
    presets = Presets(scout.storage.parent / 'filters.json')
    salaries = SalarySettings(scout.storage.parent / 'salaries.json')
    lock = threading.RLock()
    state = {'loading': False, 'progress': '', 'error': None}
    layout_path = scout.storage.parent / 'layouts.json'
    layout_columns = {'name','age','positions','club_name','ca','pa','attribute_sum','goalkeeping_sum','rating','nation_id','reputation','ability_difference','rep_home','rep_current','rep_world','wage','value','release_fee','ca_mean','pa_mean','age_mean','player_count','ca_count','pa_count','age_count','team_slot','height_cm','balance','transfer_budget_remaining','wage_budget_weekly','stadium_seated_capacity','stadium_expansion_capacity','league_name','stadium_name','model_value','model_fee'} | {f'attr_{key}' for group in GROUPS.values() for key in group}
    layout_columns.update(('eu_national','staff_role','staff_area','release_fee_domestic','release_fee_foreign'))

    def load(path):
        try:
            def progress(message):
                with lock:
                    state['progress'] = message
            scout.load(path, progress)
            with lock:
                state.update(loading=False, progress='', error=None)
        except Exception as exc:
            with lock:
                state.update(loading=False, progress='', error=f'{type(exc).__name__}: {exc}')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, body, status=200, content_type='application/json', headers=None):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            try:
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return

        def route(self):
            parsed = urlsplit(self.path)
            prefix = f'/{token}/'
            expected = f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host') != expected or not parsed.path.startswith(prefix):
                self.reply({'error': 'Acesso não autorizado.'}, 403)
                return None, None
            return parsed.path[len(prefix):], {k: v[0] for k, v in parse_qs(parsed.query).items()}

        def do_GET(self):
            path, query = self.route()
            if path is None:
                return
            try:
                if path in ('', 'index.html', 'app.js', 'style.css'):
                    file = ROOT / 'web' / (path or 'index.html')
                    self.reply(file.read_bytes(), content_type=mimetypes.guess_type(file)[0] or 'text/plain')
                    return
                with lock:
                    if path == 'api/status':
                        self.reply({**state, 'meta': scout.meta,
                                    'saves': [{'path': str(p), 'name': p.name, 'size': p.stat().st_size}
                                              for p in sorted(SAVE_DIR.glob('*.fm'), key=lambda p: p.stat().st_mtime, reverse=True)],
                                    'groups': GROUPS, 'staff_scoring_attributes': SCORING_SKILLS,
                                    'traits': [{'id': t.value, 'name': t.name.lower().replace('_', ' ')} for t in Trait if t.value >= 0],
                                    'roles': {k: {'name': v[0], 'position': v[1], 'weights': v[2]} for k, v in ROLES.items()}})
                        return
                    if path == 'api/presets':
                        self.reply({'version': 1, 'presets': presets.read()})
                        return
                    if path == 'api/layouts':
                        self.reply(read_layouts(layout_path))
                        return
                    if state['loading']:
                        self.reply({'error': 'Aguarde a leitura do save terminar.'}, 409)
                        return
                    if not scout.meta:
                        self.reply({'error': 'Abra um save primeiro.'}, 409)
                        return
                    kind = query.get('kind', 'players')
                    if kind not in scout.rows:
                        raise ValueError('Tipo de registro inválido.')
                    if path == 'api/options':
                        rows = scout.rows[kind]
                        clubs = {r['club_uid']: r.get('club_short_name') or r.get('club_name') or r.get('name')
                                 for r in rows if r.get('club_uid') is not None}
                        self.reply({'clubs': sorted([{'uid': k, 'name': v} for k, v in clubs.items()], key=lambda c: c['name'] or ''),
                                    'nations': [{'id': n, 'name': NATION_NAMES[n]} for n in sorted({n for r in rows for n in r.get('nation_ids', []) if n in NATION_NAMES})],
                                    'based': [{'id': n, 'name': NATION_NAMES[n]} for n in sorted({r['club_nation_id'] for r in rows if r.get('club_nation_id') in NATION_NAMES})],
                                    'regions': REGIONS,
                                    'staff_areas': STAFF_AREAS if kind == 'staff' else {},
                                    'staff_roles': STAFF_ROLES if kind == 'staff' else {},
                                    'competitions': scout.competitions})
                        return
                    if path == 'api/salaries':
                        self.reply(salaries.view(scout.career))
                        return
                    if path == 'api/rows':
                        validate_filter({'name': 'Pesquisa', 'kind': kind, 'filters': {k: v for k, v in query.items() if k not in ('kind', 'offset', 'limit', 'shortlist', 'columns') and not (k == 'club' and v == '-1')}})
                        selected = scout.shortlisted(kind)
                        candidates = scout.rows[kind]
                        if kind == 'clubs':
                            scope = query.get('squad_scope', 'first')
                            candidates = [{**r, **r['squad_metrics'][scope]} for r in candidates]
                        rows = filter_rows(candidates, query, selected, game_date=scout.meta['date'])
                        offset = max(0, int(query.get('offset', 0)))
                        limit = min(200, max(1, int(query.get('limit', 100))))
                        columns = ('uid', 'unique_id', 'name', 'age', 'nation_id', 'nation_name', 'eu_national', 'club_name', 'club_short_name', 'club_uid',
                                   'natural_positions', 'team_slot', 'ca', 'pa', 'attribute_sum', 'goalkeeping_sum', 'rating', 'best_role', 'contract_end',
                                   'ability_difference','rep_home','rep_current','rep_world','wage','value','release_fee','model_value_basis','model_fee_basis')
                        if kind == 'clubs':
                            columns += ('reputation','ca_mean','pa_mean','age_mean','player_count','ca_count','pa_count','age_count')
                        requested = query.get('columns', '').split(',')
                        if any(c and c not in layout_columns for c in requested):
                            raise ValueError('Coluna desconhecida.')
                        columns = tuple(set(columns) | {c for c in requested if c})
                        self.reply({'total': len(rows), 'shortlist_count': len(selected),
                                    'rows': [{**{k: column_value(r, k) for k in columns}, 'shortlisted': r['uid'] in selected} for r in rows[offset:offset+limit]]})
                        return
                    if path == 'api/profile':
                        uid = int(query['uid'])
                        row = scout.index[kind][uid]
                        history = scout.history(uid) if kind == 'players' else []
                        self.reply({'row': row, 'history': history, 'shortlisted': uid in scout.shortlisted(kind)})
                        return
                    if path == 'api/export':
                        rows = filter_rows(scout.rows[kind], {'kind': kind, 'shortlist': '1'}, scout.shortlisted(kind))
                        stream = io.StringIO()
                        writer = csv.writer(stream)
                        writer.writerow(['ID', 'Nome', 'Idade', 'Clube'])
                        for r in rows:
                            values = [r.get('unique_id'), r.get('name'), r.get('age'), r.get('club_name')]
                            writer.writerow(["'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for v in values])
                        self.reply(('\ufeff' + stream.getvalue()).encode(), content_type='text/csv; charset=utf-8',
                                   headers={'Content-Disposition': 'attachment; filename="matt-scout-lista.csv"'})
                        return
                    if path == 'api/list-file':
                        if kind not in ('players', 'staff'):
                            raise ValueError('Selecione jogadores ou staff.')
                        selected = scout.shortlisted(kind)
                        self.reply({'version': 1, 'kind': kind, 'people': [
                            {k: r.get(k) for k in ('unique_id', 'birth_date', 'name')}
                            for r in scout.rows[kind] if r['uid'] in selected]})
                        return
                self.reply({'error': 'Página não encontrada.'}, 404)
            except (ValueError, KeyError, TypeError) as exc:
                self.reply({'error': str(exc)}, 400)

        def do_POST(self):
            path, query = self.route()
            if path is None:
                return
            origin = self.headers.get('Origin')
            if origin and origin != f'http://127.0.0.1:{self.server.server_port}':
                self.reply({'error': 'Origem não autorizada.'}, 403)
                return
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length <= 2097152:
                    raise ValueError('Solicitação inválida.')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('Solicitação inválida.')
                with lock:
                    if path == 'api/layouts':
                        for key, value in body.items():
                            if key not in scout.rows or not isinstance(value, list) or not 1 <= len(value) <= 82 or 'name' not in value or any(c not in layout_columns for c in value):
                                raise ValueError('Layout inválido. Preserve a coluna Nome e use até 82 colunas.')
                        temporary = layout_path.with_suffix('.tmp')
                        temporary.write_text(json.dumps({**body, '_version': 1}))
                        temporary.replace(layout_path)
                        self.reply({'ok': True})
                        return
                    if path == 'api/presets':
                        self.reply(presets.add(body))
                        return
                    if path == 'api/presets/import':
                        self.reply({'added': presets.import_file(body)})
                        return
                    if path == 'api/presets/remove':
                        presets.remove(body['id'])
                        self.reply({'ok': True})
                        return
                    if state['loading']:
                        self.reply({'error': 'Já existe um save sendo carregado.'}, 409)
                        return
                    if path == 'api/load':
                        if not isinstance(body.get('path'), str):
                            raise ValueError('Selecione um arquivo .fm.')
                        state.update(loading=True, progress='Preparando leitura…', error=None)
                        threading.Thread(target=load, args=(body['path'],), daemon=False).start()
                        self.reply({'ok': True}, 202)
                        return
                    if path == 'api/salaries':
                        if not scout.meta:
                            raise ValueError('Abra um save primeiro.')
                        reference = None
                        if 'amount' in body or 'money_amount' in body:
                            if body.get('kind') not in ('players','staff') or type(body.get('uid')) is not int:
                                raise ValueError('Selecione um jogador ou staff para conferir a conversão.')
                            reference = scout.index[body['kind']][body['uid']]
                        self.reply(salaries.update(scout.career, body, reference))
                        return
                    if path == 'api/shortlist':
                        kind = body['kind']
                        if kind not in ('players', 'staff'):
                            raise ValueError('Tipo de registro inválido.')
                        shortlisted=scout.toggle_shortlist(kind, int(body['uid']))
                        self.reply({'shortlisted': shortlisted, 'shortlist_count': len(scout.shortlisted(kind))})
                        return
                    if path == 'api/list-import':
                        kind = body.get('kind')
                        people = body.get('people')
                        if body.get('version') != 1 or kind not in ('players', 'staff') or not isinstance(people, list) or len(people) > 10000:
                            raise ValueError('Use uma lista JSON FM Matt Scout, versão 1.')
                        if any(not isinstance(p, dict) or type(p.get('unique_id')) is not int or not (p.get('birth_date') is None or isinstance(p.get('birth_date'), str)) or not (p.get('name') is None or isinstance(p.get('name'), str)) for p in people):
                            raise ValueError('Lista inválida: cada registro precisa de ID, nome e nascimento.')
                        identities = {(r.get('unique_id'), r.get('birth_date'), r.get('name')): r['uid'] for r in scout.rows[kind] if r.get('birth_date') and r.get('name')}
                        matched = [identities.get((p['unique_id'], p['birth_date'], p['name'])) for p in people]
                        with scout.db() as db:
                            db.executemany('INSERT OR IGNORE INTO shortlist VALUES(?,?,?)', [(scout.career, kind, uid) for uid in matched if uid is not None])
                        self.reply({'matched': sum(uid is not None for uid in matched), 'missing': sum(uid is None for uid in matched)})
                        return
                self.reply({'error': 'Ação não encontrada.'}, 404)
            except (ValueError, KeyError, TypeError) as exc:
                self.reply({'error': str(exc)}, 400)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    url = f'http://127.0.0.1:{server.server_port}/{token}/'
    print(url, flush=True)
    return server, url


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--storage', type=Path)
    args = parser.parse_args()
    server, _ = serve(args.port, args.storage)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
