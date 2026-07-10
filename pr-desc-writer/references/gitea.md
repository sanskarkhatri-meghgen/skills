# Gitea Reference — PR Description Writer

Platform-specific commands for **Gitea** repos. Load this file only when the platform is Gitea.
Core workflow, scope rules, and description structure live in `SKILL.md`.

---

## Prerequisites

```bash
command -v git  >/dev/null || { echo "git is required"; exit 1; }
# Set these environment variables before running:
#   GITEA_URL    — base URL of your Gitea instance, e.g. https://gitea.example.com
#   GITEA_TOKEN  — personal access token (Settings > Applications)
#   GITEA_OWNER  — repo owner (user or org)
#   GITEA_REPO   — repo name
: "${GITEA_URL:?Set GITEA_URL}" "${GITEA_TOKEN:?Set GITEA_TOKEN}"
: "${GITEA_OWNER:?Set GITEA_OWNER}" "${GITEA_REPO:?Set GITEA_REPO}"
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

detect_base_branch() {
  # Try open PR first
  local pr_base=$(curl -s -H "Authorization: token $GITEA_TOKEN" \
    "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO/pulls?state=open&head=$CURRENT_BRANCH&limit=1" \
    | python3 -c "import sys,json; v=json.load(sys.stdin); print(v[0]['base']['ref'] if v else '')" 2>/dev/null)
  [[ -n "$pr_base" ]] && { echo "$pr_base"; return; }

  # Repo default branch
  local default=$(curl -s -H "Authorization: token $GITEA_TOKEN" \
    "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('default_branch',''))" 2>/dev/null)
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

# Check for open PR; prints PR number if found
curl -s -H "Authorization: token $GITEA_TOKEN" \
  "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO/pulls?state=open&head=$CURRENT_BRANCH&limit=1" \
  | python3 -c "import sys,json; v=json.load(sys.stdin); print(v[0]['number'] if v else '')"
```

---

## Creating & Updating PRs

```bash
# Create new PR
curl -s -H "Authorization: token $GITEA_TOKEN" -X POST \
  "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO/pulls" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Your Title\",
    \"body\": \"Your body markdown\",
    \"head\": \"$CURRENT_BRANCH\",
    \"base\": \"$BASE_BRANCH\"
  }"

# Update existing PR (replace PR_NUMBER)
PR_NUMBER=<number>
curl -s -H "Authorization: token $GITEA_TOKEN" -X PATCH \
  "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO/pulls/$PR_NUMBER" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"New Title\", \"body\": \"New body\"}"
```

---

## Closing PRs

```bash
# Close (without merging) a PR by number
PR_NUMBER=<number>
curl -s -H "Authorization: token $GITEA_TOKEN" -X PATCH \
  "$GITEA_URL/api/v1/repos/$GITEA_OWNER/$GITEA_REPO/pulls/$PR_NUMBER" \
  -H "Content-Type: application/json" \
  -d '{"state": "closed"}'

# To find the open PR number on the current branch, see PR Detection above.
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
