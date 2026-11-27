#!/usr/bin/env bash
# Run every gate, then rebase on dev and push to work/ only (the App advances dev). Stops at the first failure. Never pipe a gate.
set -euo pipefail
cd "$(dirname "$0")/.."
# DRAFT for cl-6.security review (dev-gate, IaC #35 / P19). Not in force. Agent name is hard-coded on purpose: never from the environment.
AGENT=cl-6.data
WORK="refs/heads/work/$AGENT"
# Refuse during a hold (finding 3), with uncommitted changes (finding 4: the gates must check what is
# pushed), and check every commit's Agent: trailer before the push, while it can still be amended (finding 5).
[ -e board/HOLD.md ] && { echo "board/HOLD.md exists: no release while it does" >&2; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "uncommitted changes: commit or stash them first" >&2; exit 1; }
git fetch -q origin dev
node scripts/build.mjs
node scripts/validate.mjs
node scripts/test-leak-scan.mjs
node scripts/leak-scan.mjs
node scripts/check-commits.mjs origin/dev HEAD
node scripts/test-check-signatures.mjs
# control 7: the security checks and their config run from the anchor, the commit the live site serves in /version.json
# (only the github-pages deployment writes it), never from the tree being released; the range checked starts there
last="$(git ls-remote origin "$WORK" | cut -f1)"   # expected sha for the lease: empty means the branch must not exist
trusted="$(mktemp -d)"
trust() { anchor=$(curl -fsS https://data.promptugal.news/version.json | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const c=JSON.parse(s).commit;if(!/^[0-9a-f]{40}$/.test(c||""))process.exit(1);console.log(c)})')
  git cat-file -e "$anchor^{commit}" 2>/dev/null || git fetch -q origin dev
  bash scripts/trusted-checks.sh "$anchor" HEAD "$trusted" >/dev/null; }
for i in 1 2 3 4 5; do
  git fetch -q origin dev
  git rebase -q origin/dev
  # One gate per line: under set -e a failure inside an && chain does not stop the script (specialist.code@ finding 1).
  node scripts/build.mjs >/dev/null
  node scripts/validate.mjs >/dev/null
  node scripts/leak-scan.mjs >/dev/null
  trust
  node "$trusted/leak-scan.mjs" >/dev/null
  node "$trusted/check-commits.mjs" "$anchor" HEAD >/dev/null
  node "$trusted/check-signatures.mjs" "$anchor" HEAD >/dev/null
  sha=$(git rev-parse HEAD)
  # Never dev, never main, never another ref. Explicit lease naming the sha last pushed there; no plain -f, no bare lease.
  if git push -q --force-with-lease="$WORK:$last" origin "HEAD:$WORK"; then last="$sha"; else sleep $((i * 3)); continue; fi
  deadline=$((SECONDS + 1200))
  while [ "$SECONDS" -lt "$deadline" ]; do
    cur=$(git ls-remote origin refs/heads/dev | cut -f1)
    [ "$cur" = "$sha" ] && { echo "released ${sha:0:7} to dev"; exit 0; }
    # fail tag: whole ref, non-empty result
    [ -n "$(git ls-remote origin "refs/tags/gate/$AGENT/${sha:0:12}-fail")" ] && { echo "gate refused ${sha:0:12}: stop and report" >&2; exit 1; }
    # dev moved to something that is not ours: go round again (fetch, rebase, run every gate again, push)
    git merge-base --is-ancestor "$cur" "$sha" 2>/dev/null || continue 2
    sleep 90
  done
  echo "gate did not move dev within 20 minutes" >&2; exit 1
done
echo "release failed after 5 attempts" >&2; exit 1
