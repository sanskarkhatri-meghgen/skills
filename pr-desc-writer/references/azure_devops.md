# Azure DevOps Reference — PR Description Writer

Platform-specific commands for **Azure DevOps** repos. Load this file only when the platform is Azure DevOps.
Core workflow, scope rules, and description structure live in `SKILL.md`.

---

## Prerequisites

```bash
command -v git  >/dev/null || { echo "git is required"; exit 1; }
command -v az   >/dev/null || { echo "az CLI required — https://aka.ms/installazureclilinux"; exit 1; }
az devops configure --defaults organization="$AZURE_ORG" project="$AZURE_PROJECT" >/dev/null 2>&1 || \
  { echo "Configure Azure DevOps: az devops configure --defaults organization=https://dev.azure.com/ORG project=PROJECT"; exit 1; }
# Required env vars:
#   AZURE_ORG     — e.g. https://dev.azure.com/myorg
#   AZURE_PROJECT — project name
#   AZURE_REPO    — repository name
: "${AZURE_ORG:?Set AZURE_ORG}" "${AZURE_PROJECT:?Set AZURE_PROJECT}" "${AZURE_REPO:?Set AZURE_REPO}"
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

detect_base_branch() {
  # Try open PR first
  local pr_base=$(az repos pr list --repository "$AZURE_REPO" --source-branch "$CURRENT_BRANCH" \
    --status active --query '[0].targetRefName' -o tsv 2>/dev/null | sed 's|refs/heads/||')
  [[ -n "$pr_base" ]] && { echo "$pr_base"; return; }

  # Repo default branch
  local default=$(az repos show --repository "$AZURE_REPO" --query 'defaultBranch' -o tsv 2>/dev/null | sed 's|refs/heads/||')
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

# Check for active PR; prints PR ID if found
az repos pr list --repository "$AZURE_REPO" \
  --source-branch "$CURRENT_BRANCH" --status active \
  --query '[0].pullRequestId' -o tsv 2>/dev/null
```

---

## Creating & Updating PRs

```bash
# Create new PR
az repos pr create \
  --repository "$AZURE_REPO" \
  --title "Your Title" \
  --description "Your body markdown" \
  --source-branch "$CURRENT_BRANCH" \
  --target-branch "$BASE_BRANCH"

# Update existing PR (replace PR_ID)
PR_ID=<number>
az repos pr update --id "$PR_ID" --title "New Title" --description "New body"

# Add reviewers
az repos pr reviewer add --id "$PR_ID" --reviewers email@example.com
```

---

## Closing PRs

```bash
# Abandon (close without merging) a PR
PR_ID=<number>
az repos pr update --id "$PR_ID" --status abandoned

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
