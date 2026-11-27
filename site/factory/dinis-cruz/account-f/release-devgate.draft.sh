#!/usr/bin/env bash
# Run every gate, then push to work/ only; the App advances dev. Stops at the first failure. Never pipe a gate.
set -euo pipefail
cd "$(dirname "$0")/.."
# DRAFT for cl-6.security review: final dev-gate recipe (conductor 02:49Z, IaC #34/#35, P19). Not in force. Plain push, no force, ever.
# Agent name hard-coded on purpose: never from the environment.
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
trusted="$(mktemp -d)"
trust() { anchor=$(curl -fsS https://data.promptugal.news/version.json | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const c=JSON.parse(s).commit;if(!/^[0-9a-f]{40}$/.test(c||""))process.exit(1);console.log(c)})')
  git cat-file -e "$anchor^{commit}" 2>/dev/null || git fetch -q origin dev
  bash scripts/trusted-checks.sh "$anchor" HEAD "$trusted" >/dev/null; }
for i in 1 2 3 4 5; do
  git fetch -q origin dev
  if [ "$i" = 1 ]; then
    git rebase -q origin/dev        # round 1: our commits are not pushed anywhere yet
  else
    # later rounds: pushed history is never rewritten; merge (signed, with Agent trailer), then every gate runs again
    git ls-remote --exit-code origin "$WORK" >/dev/null 2>&1 && git fetch -q origin "$WORK"
    for base in origin/dev "origin/work/$AGENT"; do
      git rev-parse -q --verify "$base" >/dev/null || continue
      git merge-base --is-ancestor "$base" HEAD || git merge -q --no-edit -m "Merge $base" -m "Agent: $AGENT@PrompTugal.dinis" "$base"
    done
  fi
  # One gate per line: under set -e a failure inside an && chain does not stop the script (specialist.code@ finding 1).
  node scripts/build.mjs >/dev/null
  node scripts/validate.mjs >/dev/null
  node scripts/leak-scan.mjs >/dev/null
  trust
  node "$trusted/leak-scan.mjs" >/dev/null
  node "$trusted/check-commits.mjs" "$anchor" HEAD >/dev/null
  node "$trusted/check-signatures.mjs" "$anchor" HEAD >/dev/null
  sha=$(git rev-parse HEAD)
  # plain push, never force, never dev or main, never another ref; refused as non-fast-forward means go round again
  git push -q origin "HEAD:$WORK" || { sleep $((i * 3)); continue; }
  deadline=$((SECONDS + 1200))
  while [ "$SECONDS" -lt "$deadline" ]; do
    [ "$(git ls-remote origin refs/heads/dev | cut -f1)" = "$sha" ] && { echo "released ${sha:0:7} to dev"; exit 0; }
    # whole-ref match, non-empty result
    [ -n "$(git ls-remote origin "refs/tags/gate/$AGENT/${sha:0:12}-fail")" ] && { echo "gate refused ${sha:0:12}: stop and report" >&2; exit 1; }
    sleep 90
  done
  echo "gate did not move dev within 20 minutes: stop and report" >&2; exit 1
done
echo "release failed after 5 attempts" >&2; exit 1
