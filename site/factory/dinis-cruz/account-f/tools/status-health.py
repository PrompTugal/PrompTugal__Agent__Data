#!/usr/bin/env python3
"""Write data/<id>/health.json for the given source ids (default: every source that has a reads.json) in a PrompTugal__News__Data checkout: what each
request of the last run was and what its status means, which requests keep failing and how often, the recent runs with the
commit that holds each and a compare link to the run before, and how many copies of the data exist. From data/<id>/reads.json
and git. No network. Run from the repo root after the collection; data/** is in cl-6.data's grant."""
import json, os, subprocess, sys, datetime, collections
REPO = 'https://github.com/PrompTugal/PrompTugal__News__Data'
MEANING = {200: 'read', 201: 'read', 404: 'not found', 403: 'refused (forbidden)', 429: 'refused (rate limited)', 401: 'refused (needs sign-in)', 'error': 'could not connect or timed out', 'too-big': 'answer larger than the size cap'}
import re
def clean(u):
    """Redact a credential in a request address before it reaches a public file (cl-6.security, 28 Nov 2026)."""
    return re.sub(r'([?&](?:key|api_?key|token|access_token|secret|sig|signature|password|pwd)=)[^&#]*', r'\1REDACTED', u or '', flags=re.I)
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def walk(d):
    n = b = 0
    for r, _, fs in os.walk(d):
        for f in fs: n += 1; b += os.path.getsize(os.path.join(r, f))
    return n, b
def meaning(x):
    if x.get('no_rules') or (x.get('status') == 404 and 'robots' in x['name'].lower()): return 'no robots.txt: the site publishes no rules (not a failure)'
    return MEANING.get(x.get('status'), 'HTTP ' + str(x.get('status')))
def commits_for(path):
    out = []
    for line in sh('git', 'log', '--format=%H%x09%cI%x09%s', '--', path).splitlines():
        h, d, s = line.split('\t', 2); out.append((h, d, s))
    return out   # newest first
API_SPEC = {  # machine-readable OpenAPI / discovery documents, verified to answer 200 on 28 Nov 2026
 'tfl-status': 'https://api.tfl.gov.uk/swagger/docs/v1', 'tfl-bikepoint': 'https://api.tfl.gov.uk/swagger/docs/v1', 'tfl-road-disruptions': 'https://api.tfl.gov.uk/swagger/docs/v1', 'tfl-jamcams': 'https://api.tfl.gov.uk/swagger/docs/v1',
 'youtube-replays': 'https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest',
 'github-pt': 'https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json'}
API_DOCS = {  # human documentation pages, verified 200 on 28 Nov 2026
 'adsb-faro': 'https://api.adsb.lol/docs', 'open-meteo-london': 'https://open-meteo.com/en/docs',
 'ea-flood': 'https://environment.data.gov.uk/flood-monitoring/doc/reference', 'ea-thames-tide': 'https://environment.data.gov.uk/flood-monitoring/doc/reference',
 'carbon-intensity-london': 'https://carbon-intensity.github.io/api-definitions/', 'euvd': 'https://euvd.enisa.europa.eu/apidoc',
 'eurostat-tourism': 'https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started',
 'contracts-finder': 'https://www.contractsfinder.service.gov.uk/apidocumentation', 'social': 'https://docs.bsky.app/docs/category/http-reference',
 'youtube-replays': 'https://developers.google.com/youtube/v3/docs'}
def advice(card, runs):
    cad = (card.get('schedule') or {}).get('cadence')
    if cad == 'once': return {'line': 'Never refreshed: a fixed archive, one read is enough.', 'basis': 'card'}
    if cad == 'daily': return {'line': 'Once a day is enough: the source itself refreshes daily.', 'basis': 'the card says the source refreshes daily'}
    n = len(runs); ch = sum(1 for r in runs if any(x.get('changed') is True for x in r['reads']))
    ts = sorted(datetime.datetime.fromisoformat(r['at'].replace('Z', '+00:00')) for r in runs)
    days = max((ts[-1] - ts[0]).total_seconds() / 86400, 0.5) if n > 1 else None
    per_day = round(ch / days, 1) if days else None
    if n < 6 or not days: line = f'Too few runs to say yet ({n} kept).'
    elif ch / n >= 0.8: line = f'The data changed on {ch} of {n} reads over {days:.0f} days: nearly every read finds new data, so it changes at least as often as it is read and reading more than twice a day would catch more states. Whether the pages that use it need them is for their owners to say.'
    elif per_day >= 4: line = f'The data changed on {ch} of {n} reads over {days:.0f} days, about {per_day} times a day (earlier runs were hourly): reading more than twice a day would catch more states. Whether the pages that use it need them is for their owners to say.'
    elif per_day >= 1.5: line = f'The data changed on {ch} of {n} reads over {days:.0f} days, about {per_day} times a day: twice a day fits.'
    else: line = f'The data changed on {ch} of {n} reads over {days:.0f} days, about {per_day} times a day: twice a day is more than needed, once a day would lose little.'
    return {'line': line, 'basis': f'suggestion derived from {n} runs in data/<id>/reads.json (a run counts as changed when any request returned different bytes than the run before); the source\'s own cadence on the card is {cad}; runs before 21 Nov were hourly', 'runs_with_change': ch, 'runs_kept': n, 'days_covered': round(days, 1) if days else None, 'changes_per_day': per_day}
SCHEDULE_TIMES = {'tz': 'Europe/Lisbon', 'times_local': ['07:03', '18:03'], 'note': 'Lisbon is UTC+0 from late October to late March, so these are also 07:03 and 18:03 UTC then; one hour earlier in UTC in summer.', 'runs_per_day': 2}
HELD = {  # sid: (list key in latest.json or None, counts key or None, what one item is, the item's date field or None)
 'adsb-faro': ('airline', None, 'airline flights', None), 'base-gov-pt': (None, 'contracts', 'public contracts', None),
 'cams': ('cameras', None, 'cameras', 'checked_at'), 'carbon-intensity-london': ('forecast', None, 'half-hour forecast points', 'from'),
 'cisa-kev': ('vulnerabilities', None, 'known exploited vulnerabilities', 'dateAdded'), 'contracts-finder': ('notices', None, 'procurement notices', 'published'),
 'ea-flood': ('stations', None, 'flood stations', None), 'ea-thames-tide': ('gauges', None, 'tidal gauges', None),
 'enisa-pubs': ('publications', None, 'publications', 'date'), 'eurostat-tourism': ('rows', None, 'figures', None),
 'euvd': ('vulnerabilities', None, 'vulnerabilities', 'published'), 'events-pt': (None, 'events', 'events', None),
 'github-pt': ('orgs', None, 'organisations', None), 'ipma-city-forecasts': ('cities', None, 'cities', 'updated'),
 'ipma-fire-risk': ('municipalities', None, 'municipalities', None), 'ipma-observations': ('stations', None, 'weather stations', None),
 'ipma-sea': ('coasts', None, 'coastal places', None), 'ipma-uv': ('places', None, 'places', None), 'ipma-warnings': (None, 'areas', 'warning areas', None),
 'meteoalarm-pt': ('messages', None, 'warning messages', 'sent_utc'), 'nvd-cve': ('cves', None, 'CVEs', 'published'), 'nvd-kev': ('cves', None, 'CVEs', 'published'),
 'open-meteo-london': ('hourly', None, 'hourly forecast points', 'time'), 'social': ('posts', None, 'posts', 'posted_at'),
 'storm-charles-archive': ('files', None, 'files', None), 'tfl-bikepoint': ('docks', None, 'cycle docks', None), 'tfl-jamcams': ('cameras', None, 'traffic cameras', 'modified'),
 'tfl-road-disruptions': ('disruptions', None, 'road disruptions', 'updated'), 'tfl-status': ('lines', None, 'lines', None), 'youtube-replays': ('videos', None, 'videos', 'published_at')}
def held(sid):
    """What the source's latest file holds: how many items, of what, the span of their dates and a count per day. From data/<id>/latest.json."""
    try: d = json.load(open(f'data/{sid}/latest.json'))
    except Exception: return None
    lk, ck, noun, df = HELD.get(sid, (None, None, 'items', None))
    items = None; dates = []
    if lk and isinstance(d.get(lk), list):
        lst = d[lk]; items = len(lst)
        if df:
            for x in lst:
                v = x.get(df) if isinstance(x, dict) else None
                if isinstance(v, str) and len(v) >= 10 and v[4] == '-' and v[7] == '-': dates.append(v[:10])
    elif ck and isinstance((d.get('counts') or {}).get(ck), int): items = d['counts'][ck]
    per = collections.Counter(dates)
    days = sorted(per.items())[-60:]
    return {'items': items, 'noun': noun, 'earliest': min(dates) if dates else None, 'latest': max(dates) if dates else None,
            'date_field': df if dates else None, 'per_day': [{'date': a, 'count': b} for a, b in days],
            'from': f'data/{sid}/latest.json' + (f' list "{lk}"' if lk else f' counts.{ck}'),
            'note': 'Dates are the items\' own dates (forecast sources hold future dates). per_day lists up to the 60 newest days. null where the items carry no date.'}
ids = sys.argv[1:] or sorted(d for d in os.listdir('data') if os.path.exists(f'data/{d}/reads.json'))
for sid in ids:
    rp = f'data/{sid}/reads.json'
    if not os.path.exists(rp): print('skip', sid); continue
    card = json.load(open(f'sources/{sid}/card.json'))
    runs = sorted(json.load(open(rp)).get('runs', []), key=lambda r: r['at'], reverse=True)
    last = runs[0]
    # how often each request failed over all runs kept
    seen = collections.defaultdict(lambda: {'runs': 0, 'bad': 0, 'status': set(), 'url': ''})
    for r in runs:
        for x in r['reads']:
            s = seen[x['name']]; s['runs'] += 1; s['url'] = x['url']
            if not (x.get('status') in (200, 201) or x.get('no_rules') or (x.get('status') == 404 and 'robots' in x['name'].lower())): s['bad'] += 1; s['status'].add(x.get('status'))
    allp = [{'request': k, 'url': clean(v['url']), 'status': sorted(v['status'], key=str), 'plain': MEANING.get(sorted(v['status'], key=str)[0], 'failed'), 'failed_in': f"{v['bad']} of {v['runs']} runs kept"} for k, v in seen.items() if v['bad']]
    cur = {x['name'] for x in last['reads'] if not (x.get('status') in (200, 201) or x.get('no_rules') or (x.get('status') == 404 and 'robots' in x['name'].lower()))}
    problems = [x for x in allp if x['request'] in cur]   # failing in the last run: what is wrong now
    earlier = [x for x in allp if x['request'] not in cur]   # failed in an older run, read fine in the last
    cm = commits_for(rp)   # a collection commit each, newest first
    def commit_for(run):
        fin = run.get('finished') or run['at']
        cand = [c for c in cm if c[1].replace('Z', '+00:00') >= fin.replace('Z', '+00:00')]
        return cand[-1] if cand else None   # the earliest commit after the run finished
    rows = []
    for i, r in enumerate(runs[:20]):
        c = commit_for(r); prev = commit_for(runs[i + 1]) if i + 1 < len(runs) else None
        rows.append({'at': r['at'], 'ok': r['ok'], 'failed': r['failed'], 'requests': len(r['reads']),
            'changed_requests': [x['name'] for x in r['reads'] if x.get('changed') is True],
            'requests_detail': [{'name': x['name'], 'status': x.get('status'), 'bytes': x.get('bytes'), 'sha256_prefix': x.get('sha256_prefix'), 'changed': x.get('changed')} for x in r['reads']],
            'failed_requests': [x['name'] for x in r['reads'] if not (x.get('status') in (200, 201) or x.get('no_rules') or (x.get('status') == 404 and 'robots' in x['name'].lower()))],
            'commit': c[0][:7] if c else None, 'commit_url': f'{REPO}/commit/{c[0]}' if c else None,
            'compare_with_previous_run_url': f'{REPO}/compare/{prev[0][:7]}...{c[0][:7]}' if c and prev and prev[0] != c[0] else None})
    nd, bd = walk(f'data/{sid}'); nv, bv = walk(f'vaults/{sid}') if os.path.isdir(f'vaults/{sid}') else (0, 0)
    tracked = len(sh('git', 'ls-files', f'vaults/{sid}').split())
    dated = sum(1 for r, _, fs in os.walk(f'vaults/{sid}') for f in fs if '/latest' not in r) if nv else 0
    doc = {'source': sid, 'title': card.get('title'), 'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
      'about': 'Why this source does or does not have a problem, from its own request log (data/<id>/reads.json) and git. Regenerated at each wake.',
      'schedule': {'card_says': (card.get('schedule') or {}).get('cadence'), 'really': 'twice a day (07:03 and 18:03 Lisbon)' if (card.get('schedule') or {}).get('cadence') not in ('daily', 'once') else ('once a day (07:03 Lisbon)' if (card.get('schedule') or {}).get('cadence') == 'daily' else 'once, never refreshed')},
      'last_run': {'at': last['at'], 'ok': last['ok'], 'failed': last['failed'],
        'requests': [{'name': x['name'], 'url': clean(x['url']), 'status': x.get('status'), 'meaning': meaning(x), 'bytes': x.get('bytes'), 'changed': x.get('changed')} for x in last['reads']]},
      'problems': problems, 'earlier_failures': earlier,
      'runs': rows,
      'copies': {'files_in_git_data': nd, 'bytes_in_git_data': bd, 'files_in_vault_working_copy': nv, 'bytes_in_vault_working_copy': bv, 'dated_copies_in_vault': dated,
        'where': {'api_latest': f'https://data.promptugal.news/api/v1/{sid}/latest.json', 'api_reads': f'https://data.promptugal.news/api/v1/{sid}/reads.json', 'source_page': f'https://data.promptugal.news/sources/{sid}/', 'git': f'{REPO}/tree/dev/data/{sid}'},
        'tracked_in_git_vaults': tracked, 'note': f'collect/lib.mjs says vaults/ is meant to stay out of git, but {tracked} files of this source are tracked in git today (earlier commits); the sgit vault holds the full history. Dinis has not yet ruled on the vaults/ question.'},
      'held': held(sid), 'cadence_advice': advice(card, runs), 'schedule_times': SCHEDULE_TIMES,
      'api_spec': API_SPEC.get(sid), 'api_docs': API_DOCS.get(sid),
      'own_page_copy': None, 'own_page_copy_note': 'not taken: a copy or screenshot of the publisher\'s page needs a rights ruling from cl-6.rights; source_home links to the page itself',
      'source_home': card.get('source_home')}
    json.dump(doc, open(f'data/{sid}/health.json', 'w'), indent=1, ensure_ascii=False); open(f'data/{sid}/health.json', 'a').write('\n')
    print(sid, 'problems', [p['request'] for p in problems], 'runs', len(rows), 'with commit', sum(1 for r in rows if r['commit']))
