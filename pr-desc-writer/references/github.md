# GitHub Reference — PR Description Writer

Platform-specific commands for **GitHub** repos. Load this file only when the platform is GitHub.
Core workflow, scope rules, and description structure live in `SKILL.md`.

---

## Prerequisites

```bash
command -v git  >/dev/null || { echo "git is required"; exit 1; }
command -v gh   >/dev/null || { echo "gh CLI required — https://cli.github.com"; exit 1; }
gh auth status  >/dev/null 2>&1 || { echo "Not authenticated — run 'gh auth login'"; exit 1; }
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
detect_base_branch() {
  local pr_base=$(gh pr view --json baseRefName --jq '.baseRefName' 2>/dev/null)
  [[ -n "$pr_base" ]] && { echo "$pr_base"; return; }

  local gh_default=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null)
  [[ -n "$gh_default" ]] && { echo "$gh_default"; return; }

  local remote_head=$(git remote show origin 2>/dev/null | grep "HEAD branch" | cut -d: -f2 | xargs)
  [[ -n "$remote_head" ]] && { echo "$remote_head"; return; }

  for branch in main master release develop; do
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
# Check for open PR on current branch
gh pr view --json number,state --jq 'if .state == "OPEN" then .number else empty end' 2>/dev/null

# Full PR details
gh pr view --json number,title,body,baseRefName,headRefName,url,state,files,commits
```

---

## Creating & Updating PRs

```bash
# Create new PR
gh pr create --title "Title" --body "$(cat <<'EOF'
...body...
EOF
)" --base "$BASE_BRANCH"

# Update existing PR (current branch)
gh pr edit --title "New Title" --body "$(cat <<'EOF'
...body...
EOF
)"

# Add reviewers / labels
gh pr edit --add-reviewer username1,username2
gh pr edit --add-label "enhancement,needs-review"
```

---

## Closing PRs

```bash
# Close (without merging) the open PR on the current branch
gh pr close

# Close a specific PR by number
gh pr close <PR_NUMBER>
```

---

## Viewing Changes

```bash
gh pr diff
gh pr view --json files --jq '.files[].path'
gh pr view --json commits --jq '.commits[] | "\(.oid[0:7]) \(.messageHeadline)"'
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
