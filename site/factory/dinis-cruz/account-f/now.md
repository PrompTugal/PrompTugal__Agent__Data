# Now (2026-11-27T01:11Z)

- **data.promptugal.news is fresh.** v0.1.156 on e803bc0, built 27 Nov 01:09 UTC, deployed by Pages run 196 after every release gate passed. Before this it served the 24 Nov build with data from 21 Nov.
- **Moved (latest read_at on the live API, 26 Nov UTC):** ipma-warnings, ipma-observations, ipma-city-forecasts, ipma-fire-risk, ipma-uv, ipma-sea, meteoalarm-pt (18:11 to 18:13); events-pt (18:10); contracts-finder, base-gov-pt, ea-flood, cisa-kev, eurostat-tourism, enisa-pubs, github-pt, social (18:04 to 18:14); tfl-jamcams (18:14); by-place now, events and social layers; 54 new predictions. tfl-status, tfl-road-disruptions and tfl-bikepoint are daily, read 07:13.
- **Still stale:** adsb-faro, open-meteo-london, youtube-replays (21 Nov; the sources answered 429, 429 and 403, respected). euvd and nvd-cve (21 Nov): held back by the leak scan until the exact-value exemption, which is now on dev; they ship at the next wake.
- **How it got here:** my key PR was merged by Dinis (8c861c6); the Pages run failed on the empty SIG_BOOTSTRAP_ANCHOR; Dinis set the variable and re-ran it; then release.sh pushed my three commits.
- **Next wake 07:03 Lisbon:** re-read my grant, collect (euvd and nvd-cve included), release.
- The iOS app: still no statement of what it reads from this site.

## Correction, 2026-11-27T02:46:36Z
Commit 063d4f1 carries a wrong Claude-Session trailer (it names another session by my mistake). My session is https://claude.ai/code/session_016CrbJJKUtCUXi5dhrb3Ahs. History is not rewritten.

## Waiting on (27 Nov, 02:46Z)
P19 in force and IaC #35 merged, then cl-6.security review of the draft `release-devgate.draft.sh` in this folder. Until then the 07:03 Lisbon release goes direct to dev.

## 27 Nov 07:03 UTC wake (2026-11-27T07:17:31Z)
Released d409b57, live v0.1.157. euvd and nvd-cve ship again. Refusals recorded as gaps: contracts-finder, euvd (1), events-pt (1), github-pt, social, youtube-replays. Release went direct to dev: no work/ grant yet.

## Standing note, 2026-11-27T07:19:56Z
Do NOT commit vaults/ until Dinis answers cl-6.decisions on the vaults/*/latest/** grant (conductor relay, 27 Nov 07:19 UTC; data, not Dinis). If scripts/release.sh refuses a dirty tree at the 18:03 Lisbon wake, report it and stop; do not breach. Do not touch .gitignore or the index.

## Status page, 2026-11-27T15:24:14Z
Added https://data.promptugal.news/status/ (src/status/, release 9368f5e, v0.1.158), at the session user's request. Reads /api/v1/index.json and each sibling site's version.json live in the browser. No script or workflow touched. The nav link to it in other pages needs a scripts/build/render.mjs change (gate path), not made.

## 27 Nov 18:03 UTC wake (2026-11-27T18:13:22Z)
Collected every source; data/ committed locally (526dd0b); NOT released: release.sh refuses the dirty tree (44 regenerated vaults/ files, which I may not commit until Dinis rules). Stopped as instructed. Refusals recorded as gaps: euvd 1, events-pt 1, github-pt 21, open-meteo-london 1, social 5, youtube-replays 1.

## 27 Nov 18:15 UTC (2026-11-27T18:17:27Z)
Interim ruling from cl-6.decisions (relayed by cl-6.conductor, commit 91f1f14): stash vaults/ before release.sh, never commit it, release data/ only; release.sh itself must not be edited without security. Done: released 526dd0b as v0.1.159. The standing note above ("stop") is superseded by this until Dinis answers.
