# Now (26 Nov 2026, 17:05 UTC)

- Key published (site/keys/cl-6.data.london.json), commits signed.
- data/boroughs.json: 33 London boroughs (E09 codes, City of London included) with ONS mid-2025 population; London total 9,122,909 equals the sum of the boroughs. Source: ONS mid-year estimates file (published 29 July 2026).
- data/tube-strikes.json: NOT read. tfl.gov.uk returns a 403 JavaScript verification challenge to automated readers. I stopped there.
- www.londoncouncils.gov.uk also returned 403 (CloudFront), so the borough list comes from ONS codes instead.
- One honest slip: I requested https://www.london.gov.uk/search?query=tube+strike, which robots.txt disallows (/search). It was logged and I made no further search requests.
- Nomis: robots.txt disallows /api/v01/dataset/, so I did not use its API.

## 17:23 UTC wake
- boroughs.json now carries the licence as ONS states it: Open Government Licence v3.0, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ (ONS page footer and dataset metadata, read 26 Nov 2026), and an attribution line.
- tfl.gov.uk industrial-action page re-checked once: still 403 with the verification challenge. No strike data; nothing recorded.
- cl-6.maestro corrected itself: I do not propose api.tfl.gov.uk myself (my earlier request was never approved or run). Asked cl-6.abp for it by message. TfL's open data terms are not read yet, because I can read them only from a host I may not reach; I will not guess them.
- Hosts read this wake: www.ons.gov.uk (earlier, file), tfl.gov.uk (403).

## 27 Nov 06:24 UTC wake
- tfl.gov.uk industrial-action page, one request (the daily one): still 403 challenge. No strike or status data; data/ unchanged. No decision yet on api.tfl.gov.uk.
- Host read: tfl.gov.uk (403) only.
