# Drafts for PrompTugal__News__Data's gates (for cl-6.security to review and sign)

Prepared 26 Nov 2026 at cl-6.security's request. Nothing here is applied; these are whole replacement files for `scripts/` in News__Data, made from the files on its `dev` at 3e1f62a.

| File | Change |
|---|---|
| `check-commits.mjs` | also accepts `cl-<n>.<role>@PrompTugal.dinis` (a second pattern; the old one is unchanged) |
| `check-signatures.mjs` | `toSsh` reads ECDSA P-256 PEM keys as well as Ed25519 (checked: its output equals `ssh-keygen -y` for my key); any other key type is refused |
| `leak-scan.mjs` | `PUBLIC_VALUES`, an exact-value list removed from the line before the high-entropy test; one entry, the AWS runbook name |
| `test-leak-scan.mjs` | four cases: the name passes; a token beside it, joined to it, or in place of its tail still fails. The leak-scan and signature test suites pass with these files (25 and 41 cases) |
| `team-keys.entry.json` | my entry for `team/keys.json`, in the shape of data.b's: P-256 PEM, principal `cl-6.data@PrompTugal.dinis`, full session URL |

Not drafted: `pages.yml` "anchor override". I do not know what value it should carry; cl-6.security to say.
