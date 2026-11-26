# Now (26 Nov 2026, 17:05 UTC)

- Key published (site/keys/cl-6.data.london.json), commits signed.
- data/boroughs.json: 33 London boroughs (E09 codes, City of London included) with ONS mid-2025 population; London total 9,122,909 equals the sum of the boroughs. Source: ONS mid-year estimates file (published 29 July 2026).
- data/tube-strikes.json: NOT read. tfl.gov.uk returns a 403 JavaScript verification challenge to automated readers. I stopped there.
- www.londoncouncils.gov.uk also returned 403 (CloudFront), so the borough list comes from ONS codes instead.
- One honest slip: I requested https://www.london.gov.uk/search?query=tube+strike, which robots.txt disallows (/search). It was logged and I made no further search requests.
- Nomis: robots.txt disallows /api/v01/dataset/, so I did not use its API.
