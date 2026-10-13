"""Read a real save through HTTP and prove the original bytes are preserved."""
import argparse
import contextlib
import hashlib
import io
import json
import tempfile
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import serve
from scout import SUM_FIELDS

parser=argparse.ArgumentParser()
parser.add_argument('save',type=Path)
args=parser.parse_args()
before=hashlib.sha256(args.save.read_bytes()).hexdigest()
start=time.monotonic()
with tempfile.TemporaryDirectory() as temp:
    with contextlib.redirect_stdout(io.StringIO()): server,url=serve(storage=Path(temp)/'scout.sqlite3')
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(path,body=None):
        data=json.dumps(body).encode() if body is not None else None
        req=urllib.request.Request(url+'api/'+path,data=data,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
    try:
        try: urllib.request.urlopen(urlsplit := url.split('/')[0]+'//'+url.split('/')[2]+'/api/status')
        except urllib.error.HTTPError as exc: assert exc.code==403
        else: raise AssertionError('An unauthenticated request was accepted')
        request('load',{'path':str(args.save)})
        deadline=time.monotonic()+90
        while True:
            status=request('status')
            if not status['loading']:break
            assert time.monotonic()<deadline,'Load exceeded 90 seconds'
            time.sleep(.2)
        assert status['error'] is None,status['error']
        meta=status['meta']
        page=request('rows?kind=players&sort=attribute_sum&direction=desc&limit=2')
        assert page['total']>1000
        person=request('profile?kind=players&uid='+str(page['rows'][0]['uid']))['row']
        assert person['attribute_sum']==sum(person['attributes'][key] for key in SUM_FIELDS)
        request('shortlist',{'kind':'players','uid':person['uid']})
        saved=request('rows?kind=players&shortlist=1');assert saved['total']==1
        bundle=request('list-file?kind=players');assert len(bundle['people'])==1
        request('shortlist',{'kind':'players','uid':person['uid']})
        restored=request('list-import',bundle);assert restored['matched']==1
        p=request('presets',{'name':'Teste de integração','kind':'players','filters':{'position':'DM','club':'318','age_min':'16','age_max':'30','attr_passing':'12','maxattr_injury_proneness':'10','sort':'attribute_sum'}})
        assert len(request('presets')['presets'])==1
        request('presets/import',request('presets'))
        assert len(request('presets')['presets'])==1
        request('layouts',{'players':['name','attribute_sum','attr_passing']})
        assert request('layouts')['players'][-1]=='attr_passing'
        columns=request('rows?kind=players&sort=attr_passing&columns=name,attr_passing&limit=2')
        assert columns['rows'][0]['attr_passing']>=columns['rows'][1]['attr_passing']
        clubs=request('rows?kind=clubs&search=Corinthians&sort=ca_mean&squad_scope=first')
        cor=next(c for c in clubs['rows'] if c['uid']==318)
        profile=request('profile?kind=clubs&uid=318')['row']
        assert cor['ca_mean']==profile['squad_metrics']['first']['ca_mean']
        assert cor['player_count']>10
        oldmeta=request('status')['meta']
        invalid=Path(temp)/'invalid.fm';invalid.write_text('This is not an FM26 save')
        request('load',{'path':str(invalid)})
        while request('status')['loading']:time.sleep(.1)
        assert request('status')['error']
        assert request('status')['meta']==oldmeta
        after=hashlib.sha256(args.save.read_bytes()).hexdigest();assert before==after,'Original save changed'
        print(json.dumps({'save':args.save.name,'build':meta['build'],'date':meta['date'],'counts':meta['counts'],
                          'warnings':meta['warnings'],'corinthians_first_team':profile['squad_metrics']['first'],
                          'original_unchanged':True,'http_security':True,'filter_file_roundtrip':True,
                          'shortlist_roundtrip':True,'invalid_save_keeps_previous':True,
                          'seconds':round(time.monotonic()-start,2)},ensure_ascii=False,indent=2))
    finally:server.shutdown();server.server_close();thread.join()
