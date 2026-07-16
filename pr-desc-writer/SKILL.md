---
name: pr-description-writer
description: >-
  Writes reviewer-friendly PR/MR descriptions built strictly from the committed diff between the
  PR base and the latest push. By default only drafts the description to PR_DESCRIPTION.md without
  touching the hosting platform; only creates, updates, or closes an actual PR/MR when the user
  explicitly asks, after confirming the target. Use this skill whenever the user wants to write,
  draft, generate, update, or summarize a PR/MR description (e.g. "write a PR description",
  "describe my changes"); open, submit, publish, or raise a PR/MR (e.g. "open a PR", "raise a PR
  targeting main"); edit an existing PR/MR's title, description, reviewers, or labels (e.g. "update
  my PR description to 'Hello'", "add reviewers to my PR"); or close, abandon, or delete a PR/MR
  (e.g. "close PR #42", "abandon my PR"). Also trigger on "prepare my branch for review" or "what
  should my PR say?".
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---
## Core Philosophy

The description represents **exactly what a reviewer will see** — the committed diff on the platform,
not the working directory. The working directory is **never** a source of truth.

**Scope** = everything committed between `BASE_BRANCH` and `origin/SOURCE_BRANCH` (the latest push of
the branch the PR is *for* — which is not always the branch currently checked out locally).
**Context** = the committed repository state at `origin/SOURCE_BRANCH`, read via Git-native commands.

Working-tree content (staged, unstaged, uncommitted) is excluded from both.

**The locally checked-out branch is never changed.** The user may ask about any branch pair (e.g.
"write a PR description for merging branch-one against main" while sitting on `branch-two`). Never run
`git checkout`, `git switch`, or anything else that alters what's checked out locally or its state —
always operate directly on remote-tracking refs (`origin/$SOURCE_BRANCH`, `origin/$BASE_BRANCH`),
regardless of what branch the user happens to be on.

**Platform detection is deferred.** Drafting a description is a pure-git operation and never needs to
know whether the remote is GitHub, GitLab, Bitbucket, etc. Platform detection only happens at the
point an actual hosting-platform action is required — see "When Platform Detection Runs" below.

---

## Hard Stops — Non-Negotiable, Never Skip These

These two checkpoints are blocking. Do not proceed past them on inferred consent, on the assumption
the user "probably wants this," or because the rest of the workflow is already in motion. Each one
requires an explicit reply from the user, sent as their own separate message, before continuing.

**A checkpoint question is not satisfied by mentioning the same information inside a summary after the
fact.** "Drafted the description from the `develop...tester` diff" is a statement, not a question, and
stating it does not fulfill Hard Stop 1 — even if the branch names are technically present in the
text. The checkpoint requires literally asking and then stopping, before the diff/description exist at
all. Likewise, "if you want, I can open the PR next" is an offer, not a yes/no question, and does not
satisfy Hard Stop 2 — do not use that phrasing or anything like it.

**Hard Stop 1 — Branch confirmation, before any diff is computed (Generation Mode only).**
`SOURCE_BRANCH` and `BASE_BRANCH` are resolved to *defaults* in Step 2 (current checkout for source,
merge-base ancestry for base). A default is not a decision. **The moment both branches are resolved,
stop.** Send a message containing only the confirmation question — nothing else, no diff output, no
`PR_DESCRIPTION.md`, no other tool calls in that same response — e.g. "I'll write this PR description
for `branch-two` into `main` — use these, or would you like different ones?" Then end the turn and
wait. Steps 3 onward (diffing, gathering context, writing the description) may only begin in a later
turn, after the user's reply arrives as its own message. **Exception:** if the user's original request
already explicitly named *both* branches (e.g. "write a PR description for merging branch-one against
main"), there is nothing left to confirm — skip straight to validation and continue in the same turn.
But if either branch is a default rather than something the user stated, the stop-and-wait is
mandatory, with no exceptions for confidence, obviousness, or time already spent.

**Hard Stop 2 — Publish confirmation, before any create/update/close of the actual PR (Generation Mode
only).** Writing `PR_DESCRIPTION.md` is not consent to publish it. Once Step 7 is done, the response
must end with a literal yes/no question naming both branches — e.g. "Do you want to merge `branch-two`
into `main` right now (yes/no)?" — and nothing after it. No platform detection, no PR-existence check,
no create/update command may run in that same response, no matter how the rest of the draft turned
out. Only an explicit affirmative arriving in the user's *next* message (e.g. "yes", "go ahead", "do
it") authorizes Step 8. The absence of a "no," moving on to another topic, or the conversation simply
continuing is **not** consent — if the next message doesn't clearly answer the question, ask again
rather than proceeding.

**Direct-Action Mode is the one exception to Hard Stop 2** — there, the user's own request ("open a PR
with description 'X'", "close PR #42") already *is* the explicit instruction to act, so no further
publish confirmation is needed on top of it. Hard Stop 1 still applies to Direct-Action create actions
whenever a branch is defaulted rather than stated (see Step 2 in that mode).

---

## Default Behavior & Routing

| Request type | Mode | Action |
|---|---|---|
| "Write/draft/generate a PR description" | Generation | Analyze diff → write `PR_DESCRIPTION.md`, report path, stop |
| "Create/open the PR" (no inline description) | Generation | Analyze diff → write description → **Hard Stop 2** → detect platform → create PR |
| "Open a PR with description 'X'" | **Direct-action** | Skip diff analysis → detect platform → use 'X' as body → create PR |
| "Update my PR description to 'X'" | **Direct-action** | Skip diff analysis → detect platform → patch open PR body to 'X' |
| "Edit my PR title to 'X'" | **Direct-action** | Skip diff analysis → detect platform → patch open PR title to 'X' |
| "Close/abandon/decline my PR" | **Direct-action** | Skip diff analysis → detect platform → close the open PR |
| "Add reviewers/labels" | **Direct-action** | Skip diff analysis → detect platform → apply changes to open PR |

Never auto-publish without user intent. See Hard Stop 2 — after writing `PR_DESCRIPTION.md`, the
"should I create the PR right now (yes/no)?" question is blocking, not a rhetorical follow-up.

---

## Safety

Read-only only. Never run, execute, import, or evaluate any file from the repository (`python x.py`,
`node x.js`, notebook cells, test suites). Understand code by reading it. If running code seems absolutely
necessary, ask the user.

---

## When Platform Detection Runs

Platform detection (identifying GitHub/GitLab/Bitbucket/Azure DevOps/AWS CodeCommit/Gitea and loading
the matching `references/${PLATFORM}.md`) is **not** an upfront step. It runs only at these two
trigger points:

1. **Direct-Action Mode** — immediately before executing the action (create/update/close/add
   reviewers-labels), since the actual API command is platform-specific.
2. **Generation Mode** — only after the user answers "yes" to "should I create the PR right now?".
   Drafting the description itself never triggers this.

### Platform Detection Procedure

Run only when one of the two triggers above is reached:

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if   echo "$REMOTE_URL" | grep -qiE "github\.com";       then PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qiE "gitlab\.com|gitlab"; then PLATFORM="gitlab"
elif echo "$REMOTE_URL" | grep -qiE "bitbucket\.(org|com)"; then PLATFORM="bitbucket"
elif echo "$REMOTE_URL" | grep -qiE "visualstudio\.com|dev\.azure\.com|azure"; then PLATFORM="azure_devops"
elif echo "$REMOTE_URL" | grep -qiE "codecommit|amazonaws\.com"; then PLATFORM="aws_codecommit"
elif echo "$REMOTE_URL" | grep -qiE "gitea|forgejo"; then PLATFORM="gitea"
else PLATFORM="unsupported"
fi

echo "Platform: $PLATFORM"
```

- If `PLATFORM="unsupported"`: stop, tell the user _"This skill supports GitHub, GitLab, Bitbucket,
  Gitea, Azure DevOps, and AWS CodeCommit. The detected remote URL (`$REMOTE_URL`) does not match
  any of these — please confirm the remote or add support."_ Do not proceed further.
- Otherwise: load `references/${PLATFORM}.md` for prerequisites (hosting CLI installed/authenticated),
  PR detection, and creating/updating/closing PRs. Do **not** read any other reference file.

Base-branch resolution and the diff/context/commit-log commands below never touch this file — they
are pure git and platform-independent.

---

## Workflow (Generation Mode)

### Step 1 — Fetch

```bash
git fetch origin --quiet
```

Stop and surface errors; never continue with stale refs. No hosting CLI check happens here — that's
deferred to the platform-detection trigger points above.

### Step 2 — Resolve Source and Base Branches, Then Confirm Both Together

Base-branch resolution is fully platform-agnostic and never hardcodes a branch name (not even
`main`/`master`). This step resolves **both** branches — the source (whose changes are being
described/merged) and the base (what it's being merged into) — and confirms them as a single pair,
per Hard Stop 1. Never confirm one without the other; a partial confirmation is not the checkpoint.

**2a. Resolve `SOURCE_BRANCH`.**

- Default: `SOURCE_BRANCH=$(git rev-parse --abbrev-ref HEAD)` — the currently checked-out branch.
- Override: if the user names a specific branch to describe/merge that differs from the current
  checkout (e.g. "write a PR description for merging branch-one against main" while sitting on
  `branch-two`), set `SOURCE_BRANCH` to the named branch directly. **Never run `git checkout` or
  `git switch` to make this true** — every subsequent command references `origin/$SOURCE_BRANCH`
  by name, so the branch never needs to be locally checked out at all.

**2b. Resolve `BASE_BRANCH`.**

- Override: if the user stated the base explicitly, use it directly.
- Default: otherwise, compute the candidate via merge-base ancestry. `SOURCE_BRANCH`'s true parent is
  whichever other branch shares the *most recent* common ancestor with it — not necessarily the
  repo's default branch. This correctly handles stacked branches (e.g. `branch-two` forked from
  `branch-one`, which forked from `main`):

```bash
git for-each-ref refs/remotes/origin --format='%(refname:short)' | while read -r ref; do
  [ "$ref" = "origin/$SOURCE_BRANCH" ] && continue
  mb=$(git merge-base "origin/$SOURCE_BRANCH" "$ref" 2>/dev/null) || continue
  ts=$(git show -s --format=%ct "$mb")
  echo "$ts $mb $ref"
done | sort -rn | head -1
```

The top result's ref (after stripping `origin/`) is the **candidate base**.

**2c. Confirm — Hard Stop 1.**

- If the user's original request already explicitly named **both** `SOURCE_BRANCH` and `BASE_BRANCH`
  (e.g. "write a PR description for merging branch-one against main"), there's nothing to confirm —
  skip straight to validation (2d).
- Otherwise, **at least one branch is a default**, and confirmation is mandatory before any diff runs.
  Send a response containing **only** this question — no diff, no scope computation, no
  `PR_DESCRIPTION.md`, nothing else in the same turn:

  > "I'll write this PR description for `branch-two` into `main` — its nearest parent looked like
  > `branch-one`, but I'm using `main` since you asked for it. Use these, or would you like different
  > ones?"

  or, when both are pure defaults:

  > "You're on `branch-two`, and its nearest parent looks like `branch-one`. I'll write the PR
  > description for `branch-two` into `branch-one` — use these, or would you like different ones?"

  **End the turn immediately after asking.** Steps 2d and 3 do not run until the user's reply arrives
  as a separate message — not later in the same response, not after a pause, not implied by silence.

**2d. Validate the chosen pair — whether from 2a/2b defaults, a partial override, or a full user override.**

Two failure conditions must be checked and surfaced clearly; do not proceed to Step 3 if either fires:

```bash
BASE="<chosen base, e.g. main>"

# Failure 1: no shared history at all
MB=$(git merge-base "origin/$BASE" "origin/$SOURCE_BRANCH" 2>/dev/null)
if [ -z "$MB" ]; then
  echo "No common ancestry found between origin/$BASE and origin/$SOURCE_BRANCH — these branches don't share history."
  exit 1
fi

# Failure 2: direction is backwards (chosen base is strictly ahead of the source branch,
# i.e. the source branch has nothing new to offer against it)
if git merge-base --is-ancestor "origin/$SOURCE_BRANCH" "origin/$BASE"; then
  echo "$SOURCE_BRANCH is behind $BASE, not ahead of it — there's nothing to diff. Did you mean to diff $BASE against $SOURCE_BRANCH instead of the other way around?"
  exit 1
fi
```

- **Failure 1** covers cases like unrelated histories, or a typo'd branch name that doesn't exist on
  the remote.
- **Failure 2** covers the "merge main onto branch-two" case — asking to diff a branch that's behind
  against one that's ahead. Report this plainly and ask the user to confirm direction rather than
  guessing.

Only once the base passes validation do `SOURCE_BRANCH` and `BASE_BRANCH` get set and Step 3 proceed.

### Step 3 — Determine PR Scope (latest push of `SOURCE_BRANCH` as reference)

The reference point is `origin/$SOURCE_BRANCH` — the last pushed commit on that branch's remote
tracking ref, **not** local `HEAD`, and regardless of whether `SOURCE_BRANCH` is the branch currently
checked out. This ensures the description reflects exactly what was pushed.

```bash
# Commits visible in the PR
git log origin/${BASE_BRANCH}..origin/${SOURCE_BRANCH} --oneline

# Files changed
git diff origin/${BASE_BRANCH}...origin/${SOURCE_BRANCH} --stat

# Full diff (scope)
git diff origin/${BASE_BRANCH}...origin/${SOURCE_BRANCH}
```

Never use `git diff` (no ref), `git diff --cached`, or `git status` to gather description content.

> **If `SOURCE_BRANCH` is the currently checked-out branch and local `HEAD` is ahead of
> `origin/$SOURCE_BRANCH`**: unpushed commits exist. Inform the user — "X commit(s) are committed
> locally but not yet pushed and are excluded from this description. Push them first if you want them
> included." Do not include them automatically. This check is skipped entirely when `SOURCE_BRANCH`
> is a different branch than the one locally checked out — there's no local `HEAD` to compare against.

### Step 4 — Note Uncommitted Changes

Only relevant when `SOURCE_BRANCH` is the branch currently checked out locally; skip this step
entirely if describing a different branch, since there is no local working tree for it to inspect.

```bash
git status --short
```

If dirty, inform the user and offer to wait for them to commit + push before regenerating. Never fold
working-tree changes into the description.

### Step 5 — Gather Architectural Context

Read the repository state at **`origin/$SOURCE_BRANCH`** (not local `HEAD`, not the filesystem):

```bash
git show origin/${SOURCE_BRANCH}:path/to/file.py        # read a file
git ls-tree -r --name-only origin/${SOURCE_BRANCH}      # list structure
git grep -n "<pattern>" origin/${SOURCE_BRANCH}         # search
```

Use this to understand *why* changes were made — surrounding architecture, patterns, data flow. Do
not use the filesystem (`Read`/`Glob`/`Grep`) for anything that feeds the description.

### Step 6 — Review Commit Messages

```bash
git log origin/${BASE_BRANCH}..origin/${SOURCE_BRANCH} --format="%h %s%n%b" | head -100
```

### Step 7 — Write the Description

Use the template below. Write to `PR_DESCRIPTION.md` and report the path. Then ask, naming both
branches explicitly, as a literal yes/no question: "Do you want to merge `$SOURCE_BRANCH` into
`$BASE_BRANCH` right now (yes/no)?" **Do not phrase this as a soft offer** — "if you want, I can open
the PR next" or similar is not the required question and does not count as asking. **This is Hard
Stop 2 — end the turn here and wait for the user's reply.** Do not call Platform Detection, do not
check for an open PR, and do not run any create/update command in the same turn as writing the
description, regardless of how confident the description is or how clearly the user's original
request implied they wanted it published.

### Step 8 (Publish only, triggered by an explicit "yes" in a later message) — Detect Platform, Then Check for Existing Open PR/MR

Only reached once the user has explicitly replied "yes" (or equivalent affirmative) to the Step 7
question, in a message of their own. Run Platform Detection (above), then see
`references/${PLATFORM}.md → PR Detection`. Closed/merged PRs are never treated as active targets.
Use the same `$SOURCE_BRANCH` and `$BASE_BRANCH` resolved and validated in Step 2 when creating the
PR — regardless of what branch is currently checked out locally.

---

## Direct-Action Mode

Activated when the user provides an **explicit inline description or title**, or requests a **close/abandon/decline** action, or asks to manage reviewers/labels.

**When to enter Direct-Action Mode:**
- The user's message contains quoted or explicit description text (e.g. `"with the description 'Hello'"`)
- The user asks to close, abandon, decline, cancel, or delete the PR
- The user asks to add reviewers or labels only (no description change implied)

**Steps in Direct-Action Mode:**

1. **Fetch** — `git fetch origin --quiet` (always required; no hosting CLI check yet).
2. **Resolve source and base branches (create only)** — for a *create* action, resolve `SOURCE_BRANCH`
   and `BASE_BRANCH` exactly as in Step 2a–2d: default `SOURCE_BRANCH` to the current checkout unless
   the user explicitly names a different branch to open the PR *for*. If the user's request named
   **both** branches explicitly (e.g. "create a PR with the description 'hello' to merge branch-two
   with main" while sitting on `branch-one` — here `SOURCE_BRANCH=branch-two`, `BASE_BRANCH=main`, and
   the local checkout stays on `branch-one` throughout), nothing needs confirming — validate (2d) and
   proceed. If either branch was left to default instead of being named, **Hard Stop 1 still
   applies**: state both resolved branches and wait for the user's reply before executing the create
   action. Never run `git checkout`/`git switch` to satisfy any of this. Skip this whole step for
   close/update/reviewers/labels-only actions, since those target an already-existing PR and don't
   need a base.
3. **Skip diff/context/commit-log steps** — do NOT run diff, stat, context, or commit-log commands;
   Direct-Action Mode never analyzes the diff.
4. **Detect platform** — run Platform Detection now, immediately before the action, since this is the
   point the hosting CLI is actually needed.
5. **Check for an existing open PR** — see `references/${PLATFORM}.md → PR Detection` (required for
   update/close/reviewers-labels; for create, verify none exists first and warn the user if one does).
   For update/close/reviewers/labels actions, the target branch is whichever branch the user names
   (e.g. "close the PR for branch-two"); if none is named, use the currently checked-out branch.
6. **Execute the action** using the command from `references/${PLATFORM}.md`:

| Intent | Command section to use |
|---|---|
| Create new PR with inline description | `Creating & Updating PRs → Create` |
| Update open PR description/title | `Creating & Updating PRs → Update` |
| Close/abandon/decline PR | `Closing PRs` |
| Add reviewers/labels | `Creating & Updating PRs → reviewers/labels` |

**Inline description extraction rules:**
- Use text inside quotes as the exact PR body (preserve as-is, no reformatting).
- If the user provides a title separately (e.g. `"titled 'Fix auth'"`), use it; otherwise prompt for one or derive from `$SOURCE_BRANCH`'s name.
- If the user says close/abandon/update but gives no branch or PR number, target the PR for the currently checked-out branch.
- If the user names an explicit source and/or base branch that differs from the current checkout, use those named branches for the action and never switch the local checkout to match them.

> **Note:** Direct-Action Mode never writes `PR_DESCRIPTION.md` unless the user also asks for a local copy.

---

## PR Description Structure

Real-world PRs are short and scannable. The section **order and headers below are fixed and must be
identical on every run** — this is what makes output reproducible. Only the table row *count* and the
presence of How to Test / Notes vary with the PR's actual complexity.

```markdown
## Summary
<!-- 2–4 sentences: what this PR does. Always present. -->

## Rationale
<!-- 1–3 sentences: why this approach, why now — the business/product reason, not implementation detail. Always present. -->

## Changes
| Change | Detail |
|---|---|
| <one specific, concrete change> | <what changed, in this one spot> |
| <one specific, concrete change> | <what changed, in this one spot> |

## How to Test
<!-- Automated: paste the exact command(s) -->
<!-- Manual: numbered steps only if commands aren't enough -->

## Notes
<!-- Breaking changes, deploy steps, env vars, migrations, open questions.
     Omit this section entirely if there's nothing worth flagging. -->
```

### Guidance by Section (fixed, deterministic — do not deviate)

**Summary** — always its own section, always first. Never merge it into Rationale or Changes.

**Rationale** — always its own section, always second, always separate from Summary. This is the
"why," never the "what." If the diff gives no clear reason, write "Not stated in commits/diff" rather
than inventing one.

**Changes table** — **one row per atomic, concrete change** (one function, one endpoint, one config
key, one behavior). Never collapse changes under an abstract category label (e.g. a row titled
"Security" or "Robustness" with several bullets stuffed into one cell) — that grouping is the exact
inconsistency to avoid. If two changes are both security-related, they still get two separate rows,
each naming the specific thing that changed. Row order follows the order changes appear in
`git diff --stat`, not by theme or importance — this is what keeps ordering reproducible run to run.
If there's only one change, the table still has exactly one row; never replace the table with prose.

**How to Test**
- Automated first, with the exact copy-pasteable command.
- Manual steps only when a human action is genuinely required.
- Omit this whole section if there is nothing to test.

**Notes** — use only when something would surprise the reviewer:
- Breaking API/contract change
- Required env vars or config before deploy
- Migration that needs a manual step
- Known limitation or follow-up ticket

**Diagrams** — include an ASCII or Mermaid diagram only when a flow is genuinely hard to follow from
the table alone (e.g. multi-step pipelines, state machines). Skip for simple CRUD changes. When
included, place it inside the Changes section, directly under the table.

### When to Add Diagrams

| Scenario | Format |
|---|---|
| Decision tree / branching logic | ASCII tree |
| Multi-step pipeline | Box diagram or Mermaid flowchart |
| State machine | Mermaid stateDiagram |
| Simple linear flow | Skip — use prose |

---

## Anti-Patterns to Avoid

1. **Wall of text** — use the table; avoid long paragraphs.
2. **Vague descriptions** — "misc fixes" tells reviewers nothing.
3. **Describing uncommitted or unpushed work** — scope is `origin/BASE_BRANCH...origin/SOURCE_BRANCH`, always.
4. **Listing every file** — the Changes table groups by area, not file.
5. **Hardcoded base branch** — always resolve via merge-base ancestry + user confirmation; never assume `main`/`master`.
6. **Diagram for everything** — only when the flow is non-obvious.
7. **Describing only the latest commit** — cover all commits in the push range.
8. **Detecting the platform too early** — never run Platform Detection during drafting; only at the confirmed-publish or direct-action trigger points.
9. **Skipping base validation** — never diff against a base with no shared history, or in the wrong direction, without surfacing the problem to the user first.
10. **Switching the local checkout** — never run `git checkout`/`git switch` to satisfy a named source or base branch that differs from what's currently checked out; always reference `origin/$SOURCE_BRANCH` and `origin/$BASE_BRANCH` directly instead.
11. **Proceeding to diff on defaulted branches without confirming (Hard Stop 1)** — if either `SOURCE_BRANCH` or `BASE_BRANCH` came from a default rather than the user's own words, confirm both together before Step 3 runs.
12. **Publishing without an explicit "yes" (Hard Stop 2)** — writing `PR_DESCRIPTION.md` is never itself consent; treat Step 7's question as blocking and end the turn there in Generation Mode.

---

## Output

**First: determine which mode applies.**

### Generation Mode (default)
1. Fetch (Step 1).
2. Resolve `SOURCE_BRANCH` and `BASE_BRANCH` (defaults: current checkout / merge-base ancestry, or
   whatever the user named explicitly). If either is a default rather than user-stated, present both
   together and wait for the user's reply — **Hard Stop 1**. Then validate (Step 2).
3. Compute scope from `origin/BASE_BRANCH...origin/SOURCE_BRANCH` (Step 3).
4. Note unpushed local commits if any and `SOURCE_BRANCH` is the current checkout (Step 3 note).
5. Note uncommitted changes if any and `SOURCE_BRANCH` is the current checkout (Step 4).
6. Gather context from `origin/$SOURCE_BRANCH` via Git-native commands (Step 5).
7. Review commit messages (Step 6).
8. Write the description using the template above (Step 7).
9. Self-check: cross-reference the file list and feature claims against `--stat` and commit log.
10. Write to `PR_DESCRIPTION.md` (or user-specified path):

```bash
cat > PR_DESCRIPTION.md << 'EOF'
<full PR description markdown>
EOF
```

Report the file path. Ask the user, naming both branches: "Do you want to merge `$SOURCE_BRANCH` into
`$BASE_BRANCH` right now (yes/no)?" — **Hard Stop 2. End the turn here.** Do not detect the platform,
check for an open PR, or run any create/update command until the user's next message explicitly says
yes.

11. **Only once that explicit "yes" arrives, in its own message**: run Platform Detection, check for
    an existing open PR (Step 8), then use the create or update command from `references/${PLATFORM}.md`,
    passing the same `$SOURCE_BRANCH`/`$BASE_BRANCH` resolved and validated in Step 2. Never switch the
    local checkout to do this.
12. Be ready to iterate based on user feedback.

### Direct-Action Mode
1. Fetch (`git fetch origin --quiet`).
2. Resolve `SOURCE_BRANCH`/`BASE_BRANCH`, but only for a create action; skip for
   close/update/reviewers/labels-only. If the user's request named both branches explicitly, validate
   and proceed. If either was left to default, Hard Stop 1 still applies — confirm both before
   executing the create. The local checkout never changes either way.
3. Skip diff/stat/context/commit-log commands entirely.
4. Detect platform now, immediately before acting.
5. Check for open PR, targeting whichever branch the user named (or the current checkout if none was named).
6. Execute the action directly (create with inline body, update title/body, close, or manage reviewers/labels).
7. Report the result (PR URL, PR number, or confirmation of closure). Do **not** write `PR_DESCRIPTION.md`.