# github-pt removal (the session user, 28 Nov 2026: "we do not need code from Portuguese organisations on GitHub")

Apply together with `github-pt-removal-scripts.patch` (preview tile, licence entry, consolidated cyber group):

    git rm -r sources/github-pt data/github-pt      # card, collector, orgs.json; latest, reads, health. History stays in git.

Dependents found by cl-6.dev and re-checked: scripts/build/{preview,licence,consolidated}.mjs (patched), sources/github-pt, data/github-pt,
data/run.json (rewritten by the next collection, no github-pt entry), src/status (changelog line, files.json regenerated).
NOT in cl-6.data's write grant, so not done: register/sources.json (entry "github-api", rendered at /api/v1/sources/github-api.json),
docs/threat-models/{github-pt.md,README.md}, board/team/data/{status.json,debriefs/*}, board/team/data-portugal/HANDOVER.md.
The website repo only mentions it in newsroom snapshots (no feed consumer). The build and validator pass without those edits.
