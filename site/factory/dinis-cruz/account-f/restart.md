# Restart: how a new session continues as cl-6.data

1. Read `agent.json`, `now.md`, `role.md`, `learnings.md` here, then `history/PROVENANCE.md` and the latest debrief of data.b: `history/repos/PrompTugal__News__Data/board/team/data/debriefs/2026-11-21-data-b-twice-daily.md`, and its `status.json` (asks and next steps).
2. Read PrompTugal__News__Website CLAUDE.md and `board/guidance/README.md` ("New from Dinis"), read-only, never push there.
3. Attach PrompTugal__News__Data with push (`add_repo`), clone it, read its CLAUDE.md and REALITY.md. Work on `dev` only.
4. Make your own key (openssl: P-256 signing, RSA-4096 encryption; private halves mode 600 in the scratchpad), publish `site/keys/<you>.json` alone in its own commit; set `gpg.format ssh`, `gpg.ssh.program ssh-keygen` (install `openssh-client` if missing), `user.signingkey`, `commit.gpgsign true` in each clone; trailers `Agent:` and `Claude-Session:` on every commit.
5. Collect: `NODE_USE_ENV_PROXY=1 node collect/run.mjs` in News__Data, then build, validate, leak scan, commit `data/`, push once, and wait for `/version.json` to show it.
6. Keep `agent.json` current: the conductor and cl-6.maestro read it instead of messaging.
