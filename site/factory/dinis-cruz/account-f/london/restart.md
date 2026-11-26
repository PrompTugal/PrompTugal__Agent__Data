# Restart: continue as cl-6.data.london

1. Read agent.json, role.md, now.md here and the grant given by cl-6.maestro.
2. Make a new session key if the old one is gone (openssl, P-256 signing, RSA-4096 encryption, private halves mode 600 outside the repository); install openssh-client (apt-get update first) for git signing.
3. Check robots.txt before any new path; log each request with get-style logging into network-log.jsonl.
4. Retry TfL only if Dinis has opened another route; refresh boroughs.json when ONS publishes mid-2026 (summer 2027).
5. Dev branch only. Tell cl-6.place.london when a data file changes.
