# AWS CodeCommit Reference — PR Description Writer

Platform-specific commands for **AWS CodeCommit** repos. Load this file only when the platform is AWS CodeCommit.
Core workflow, scope rules, and description structure live in `SKILL.md`.

---

## Prerequisites

```bash
command -v git >/dev/null  || { echo "git is required"; exit 1; }
command -v aws >/dev/null  || { echo "AWS CLI required — https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || { echo "AWS credentials not configured — run 'aws configure'"; exit 1; }
# Required env var:
#   CC_REPO — CodeCommit repository name
#   CC_REGION — AWS region (default: pulled from AWS config)
: "${CC_REPO:?Set CC_REPO}"
CC_REGION="${CC_REGION:-$(aws configure get region)}"
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

detect_base_branch() {
  # Try open PR first
  local pr_ids=$(aws codecommit list-pull-requests --repository-name "$CC_REPO" \
    --pull-request-status OPEN --region "$CC_REGION" \
    --query 'pullRequestIds' --output text 2>/dev/null)
  for id in $pr_ids; do
    local src=$(aws codecommit get-pull-request --pull-request-id "$id" --region "$CC_REGION" \
      --query 'pullRequest.pullRequestTargets[0].sourceReference' --output text 2>/dev/null)
    if [[ "$src" == "refs/heads/$CURRENT_BRANCH" ]]; then
      aws codecommit get-pull-request --pull-request-id "$id" --region "$CC_REGION" \
        --query 'pullRequest.pullRequestTargets[0].destinationReference' --output text 2>/dev/null \
        | sed 's|refs/heads/||'
      return
    fi
  done

  # Repo default branch
  local default=$(aws codecommit get-repository --repository-name "$CC_REPO" --region "$CC_REGION" \
    --query 'repositoryMetadata.defaultBranch' --output text 2>/dev/null)
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

# List open PR IDs, then find the one targeting current branch
aws codecommit list-pull-requests \
  --repository-name "$CC_REPO" \
  --pull-request-status OPEN \
  --region "$CC_REGION" \
  --query 'pullRequestIds' --output text
```

---

## Creating & Updating PRs

```bash
# Create new PR
aws codecommit create-pull-request \
  --title "Your Title" \
  --description "Your body markdown" \
  --targets "repositoryName=$CC_REPO,sourceReference=$CURRENT_BRANCH,destinationReference=$BASE_BRANCH" \
  --region "$CC_REGION"

# Update existing PR (replace PR_ID)
PR_ID=<id>
aws codecommit update-pull-request-title --pull-request-id "$PR_ID" --title "New Title" --region "$CC_REGION"
aws codecommit update-pull-request-description --pull-request-id "$PR_ID" --description "New body" --region "$CC_REGION"
```

---

## Closing PRs

```bash
# Close (without merging) a PR — CodeCommit calls this "closing" the PR
PR_ID=<id>
aws codecommit update-pull-request-status \
  --pull-request-id "$PR_ID" \
  --pull-request-status CLOSED \
  --region "$CC_REGION"

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
