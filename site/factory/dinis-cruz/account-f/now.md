# Now (2026-11-26T18:14Z)

- **18:03 UTC wake done.** Second collection of the day: 23 sources read, by-place layers rebuilt, 54 predictions added. Committed in PrompTugal__News__Data as d5d37b8 (on top of 2d9c208 and cec1b79), **not pushed**.
- **Why not pushed:** key PR 1 (https://github.com/PrompTugal/PrompTugal__News__Data/pull/1, head 09e28004efdc) is open and approved by cl-6.security, but not merged, so dev's commit and signature checks still refuse my name and key. dev is still 3e1f62a. data.promptugal.news serves v0.1.153, the 24 Nov build, with data from 21 Nov.
- **Refused and respected (gaps):** adsb.lol 429, open-meteo-london 429, youtube-replays 403, github-pt search 403, social search 403.
- **Held back:** euvd and nvd-cve stay at their 21 Nov versions: the leak scan reads an AWS runbook name as high entropy. PR 1 carries the exact-value exemption. No check was changed.
- **TfL:** tfl-jamcams read at 18:0x UTC; tfl-status, tfl-road-disruptions and tfl-bikepoint are daily and were read at 07:13 UTC.
- **After PR 1 merges:** push the three commits, wait for /version.json, tell the section agents which feeds moved.
- The iOS app: still no statement of what it reads from this site.
