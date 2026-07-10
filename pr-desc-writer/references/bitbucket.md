# Bitbucket Reference — PR Description Writer

Platform-specific commands for **Bitbucket** repos. Load this file only when the platform is Bitbucket.
Core workflow, scope rules, and description structure live in `SKILL.md`.

---

## Prerequisites

```bash
command -v git  >/dev/null || { echo "git is required"; exit 1; }
# Bitbucket has no widely-adopted first-party CLI; use the REST API via curl.
# Set these environment variables before running:
#   BB_USER     — Bitbucket username
#   BB_TOKEN    — App password (Settings > App passwords, scope: Repositories + Pull requests)
#   BB_WORKSPACE — workspace slug
#   BB_REPO      — repo slug (usually the last path segment of the repo URL)
: "${BB_USER:?Set BB_USER}" "${BB_TOKEN:?Set BB_TOKEN}"
: "${BB_WORKSPACE:?Set BB_WORKSPACE}" "${BB_REPO:?Set BB_REPO}"
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

detect_base_branch() {
  # Try open PR first
  local pr_base=$(curl -s -u "$BB_USER:$BB_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=source.branch.name%3D%22$CURRENT_BRANCH%22%20AND%20state%3D%22OPEN%22&fields=values.destination.branch.name" \
    | python3 -c "import sys,json; v=json.load(sys.stdin).get('values',[]); print(v[0]['destination']['branch']['name'] if v else '')" 2>/dev/null)
  [[ -n "$pr_base" ]] && { echo "$pr_base"; return; }

  # Repo default branch
  local default=$(curl -s -u "$BB_USER:$BB_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO?fields=mainbranch.name" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('mainbranch',{}).get('name',''))" 2>/dev/null)
  [[ -n "$default" ]] && { echo "$default"; return; }

  for branch in main master develop; do
    git rev-parse --verify "origin/$branch" &>/dev/null && { echo "$branch"; return; }
  done
  echo "main"
}
BASE_BRANCH=$(detect_base_branch)
```

---

## Scope Commands

```bash
# Commits in the PR (since last push to remote branch)
git log origin/${BASE_BRANCH}..origin/HEAD --oneline

# Files changed
git diff origin/${BASE_BRANCH}...origin/HEAD --stat

# Full diff
git diff origin/${BASE_BRANCH}...origin/HEAD
```

---

## Architectural Context

```bash
# Read file from the last-pushed commit
git show origin/HEAD:path/to/file.py

# List committed tree
git ls-tree -r --name-only origin/HEAD

# Search committed tree
git grep -n "<pattern>" origin/HEAD
```

---

## PR Detection & Info

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check for open PR; prints PR ID if found
curl -s -u "$BB_USER:$BB_TOKEN" \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=source.branch.name%3D%22$CURRENT_BRANCH%22%20AND%20state%3D%22OPEN%22&fields=values.id" \
  | python3 -c "import sys,json; v=json.load(sys.stdin).get('values',[]); print(v[0]['id'] if v else '')"
```

---

## Creating & Updating PRs

```bash
# Create new PR
curl -s -u "$BB_USER:$BB_TOKEN" -X POST \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Your Title\",
    \"description\": \"Your body markdown\",
    \"source\": {\"branch\": {\"name\": \"$CURRENT_BRANCH\"}},
    \"destination\": {\"branch\": {\"name\": \"$BASE_BRANCH\"}}
  }"

# Update existing PR (replace PR_ID)
PR_ID=<number>
curl -s -u "$BB_USER:$BB_TOKEN" -X PUT \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$PR_ID" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"New Title\", \"description\": \"New body\"}"
```

---

## Closing PRs

```bash
# Decline (close without merging) a PR by ID
PR_ID=<number>
curl -s -u "$BB_USER:$BB_TOKEN" -X POST \
  "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$PR_ID/decline"

# To find the open PR ID on the current branch, see PR Detection above.
```

---

## Common Patterns

### Feature Flag
```markdown
## Feature Flag
Controlled by `FEATURE_FLAG_NAME` (default: `False`).
- **On:** Behavior A, Behavior B
- **Off:** Falls back to original behavior
```

### Migrations
```markdown
## Migrations
| Migration | Description | Reversible |
|-----------|-------------|------------|
| `0001_add_field.py` | Adds `new_field` to Model | Yes |

**Rollback:** `./manage.py migrate app_name 0000_previous`
```

### API Changes
```markdown
## API Changes
| Method | Path | Change |
|--------|------|--------|
| `GET` | `/api/v2/resource` | New endpoint |
| `GET` | `/api/v1/old` | **Deprecated** — use v2 |
```
