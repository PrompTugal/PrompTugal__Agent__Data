#!/usr/bin/env python3
"""Write src/status/files.json in a PrompTugal__News__Data checkout: per source, the topic, the card's cadence, the schedule it is
really collected on, how many files and bytes it holds in data/ and vaults/, the files the last collection wrote, and the items
its latest file reports. Run from the repo root at each wake, after the collection. No network."""
import json, os, re, subprocess, sys, datetime
TOPIC = {
 'Weather and sea, Portugal': ['ipma-city-forecasts','ipma-fire-risk','ipma-observations','ipma-sea','ipma-uv','ipma-warnings','meteoalarm-pt'],
 'London: transport, rivers, weather, energy': ['tfl-status','tfl-bikepoint','tfl-road-disruptions','tfl-jamcams','ea-flood','ea-thames-tide','open-meteo-london','carbon-intensity-london'],
 'Cyber': ['cisa-kev','nvd-cve','nvd-kev','euvd','enisa-pubs','github-pt'],
 'Public money and economy': ['base-gov-pt','contracts-finder','eurostat-tourism'],
 'Events, social and video': ['events-pt','social','youtube-replays'],
 'Flights and cameras, Portugal': ['adsb-faro','cams'],
 'Archive': ['storm-charles-archive'],
}
topic_of = {s:t for t,v in TOPIC.items() for s in v}
def walk(d):
    n=b=0
    for r,_,fs in os.walk(d):
        for f in fs: n+=1; b+=os.path.getsize(os.path.join(r,f))
    return n,b
def sh(*a): return subprocess.run(a,capture_output=True,text=True).stdout
# the last commit that touched data/ is the last collection
last=sh('git','log','-1','--format=%H','--','data').strip()
changed={}
for line in sh('git','show','--name-status','--format=',last,'--','data').splitlines():
    st,_,path=line.partition('\t'); parts=path.split('/')
    if len(parts)>2: changed.setdefault(parts[1],{'A':0,'M':0,'D':0}); changed[parts[1]][st[0] if st[0] in 'AMD' else 'M']+=1
def items(sid):
    try: d=json.load(open(f'data/{sid}/latest.json'))
    except Exception: return None,None
    c=d.get('counts') if isinstance(d,dict) else None
    if isinstance(c,dict):
        for k,v in c.items():
            if isinstance(v,int) and not isinstance(v,bool): return v,'counts.'+k
    return None,None
out=[]
for d in sorted(os.listdir('sources')):
    cp=f'sources/{d}/card.json'
    if not os.path.exists(cp): continue
    c=json.load(open(cp)); sid=c['id']; cad=(c.get('schedule') or {}).get('cadence','')
    # the real schedule: the wake runs 07:03 and 18:03 Lisbon; daily and once sources are collected once, at 07:03
    real='once, never refreshed' if cad=='once' else ('once a day (07:03 Lisbon)' if cad=='daily' else 'twice a day (07:03 and 18:03 Lisbon)')
    nd,bd=walk(f'data/{sid}') if os.path.isdir(f'data/{sid}') else (0,0)
    nv,bv=walk(f'vaults/{sid}') if os.path.isdir(f'vaults/{sid}') else (0,0)
    it,how=items(sid); ch=changed.get(sid,{})
    out.append({'id':sid,'title':c.get('title'),'topic':topic_of.get(sid,'Other'),'region':c.get('region'),'card_cadence':cad,'actual_schedule':real,
      'card_matches':(cad in ('daily','once')) or False,'files_data':nd,'bytes_data':bd,'files_vault':nv,'bytes_vault':bv,
      'last_run_files_added':ch.get('A',0),'last_run_files_changed':ch.get('M',0),'items':it,'items_from':how})
doc={'about':'Files, bytes and the real collection schedule per source, counted in the data repository at the last wake. Regenerated at each wake by cl-6.data. Items are the first count a source file reports about itself, not comparable between sources.',
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'last_collection_commit':last[:7],
 'schedule':'The collection runs at 07:03 and 18:03 Lisbon. Sources the card lists as hourly or every 6 hours are read at both runs; daily sources at the first only. The cards still describe an older hourly schedule.',
 'sources':out}
os.makedirs('src/status',exist_ok=True)
json.dump(doc,open('src/status/files.json','w'),indent=1,ensure_ascii=False); open('src/status/files.json','a').write('\n')
print(len(out),'sources; topics',sorted({o['topic'] for o in out}),'; total files',sum(o['files_data']+o['files_vault'] for o in out))
