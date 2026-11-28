#!/usr/bin/env python3
"""Write data/<id>/health.json for the given source ids (default: euvd social) in a PrompTugal__News__Data checkout: what each
request of the last run was and what its status means, which requests keep failing and how often, the recent runs with the
commit that holds each and a compare link to the run before, and how many copies of the data exist. From data/<id>/reads.json
and git. No network. Run from the repo root after the collection; data/** is in cl-6.data's grant."""
import json, os, subprocess, sys, datetime, collections
REPO = 'https://github.com/PrompTugal/PrompTugal__News__Data'
MEANING = {200: 'read', 201: 'read', 404: 'not found', 403: 'refused (forbidden)', 429: 'refused (rate limited)', 401: 'refused (needs sign-in)', 'error': 'could not connect or timed out', 'too-big': 'answer larger than the size cap'}
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
ids = sys.argv[1:] or ['euvd', 'social']
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
    problems = [{'request': k, 'url': v['url'], 'status': sorted(v['status'], key=str), 'plain': MEANING.get(sorted(v['status'], key=str)[0], 'failed'), 'failed_in': f"{v['bad']} of {v['runs']} runs kept"} for k, v in seen.items() if v['bad']]
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
            'failed_requests': [x['name'] for x in r['reads'] if not (x.get('status') in (200, 201) or x.get('no_rules') or (x.get('status') == 404 and 'robots' in x['name'].lower()))],
            'commit': c[0][:7] if c else None, 'commit_url': f'{REPO}/commit/{c[0]}' if c else None,
            'compare_with_previous_run_url': f'{REPO}/compare/{prev[0][:7]}...{c[0][:7]}' if c and prev and prev[0] != c[0] else None})
    nd, bd = walk(f'data/{sid}'); nv, bv = walk(f'vaults/{sid}') if os.path.isdir(f'vaults/{sid}') else (0, 0)
    dated = sum(1 for r, _, fs in os.walk(f'vaults/{sid}') for f in fs if '/latest' not in r) if nv else 0
    doc = {'source': sid, 'title': card.get('title'), 'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
      'about': 'Why this source does or does not have a problem, from its own request log (data/<id>/reads.json) and git. Regenerated at each wake.',
      'schedule': {'card_says': (card.get('schedule') or {}).get('cadence'), 'really': 'twice a day (07:03 and 18:03 Lisbon)' if (card.get('schedule') or {}).get('cadence') not in ('daily', 'once') else 'once a day (07:03 Lisbon)'},
      'last_run': {'at': last['at'], 'ok': last['ok'], 'failed': last['failed'],
        'requests': [{'name': x['name'], 'url': x['url'], 'status': x.get('status'), 'meaning': meaning(x), 'bytes': x.get('bytes'), 'changed': x.get('changed')} for x in last['reads']]},
      'problems': problems,
      'runs': rows,
      'copies': {'files_in_git_data': nd, 'bytes_in_git_data': bd, 'files_in_vault_working_copy': nv, 'bytes_in_vault_working_copy': bv, 'dated_copies_in_vault': dated,
        'where': {'api_latest': f'https://data.promptugal.news/api/v1/{sid}/latest.json', 'api_reads': f'https://data.promptugal.news/api/v1/{sid}/reads.json', 'source_page': f'https://data.promptugal.news/sources/{sid}/', 'git': f'{REPO}/tree/dev/data/{sid}'},
        'note': 'vaults/ is described in collect/lib.mjs as never in git; some of its files are tracked today and the sgit vault holds the full history.'},
      'source_home': card.get('source_home')}
    json.dump(doc, open(f'data/{sid}/health.json', 'w'), indent=1, ensure_ascii=False); open(f'data/{sid}/health.json', 'a').write('\n')
    print(sid, 'problems', [p['request'] for p in problems], 'runs', len(rows), 'with commit', sum(1 for r in rows if r['commit']))
