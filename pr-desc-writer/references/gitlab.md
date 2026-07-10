# GitLab Reference — PR Description Writer

Platform-specific commands for **GitLab** repos (Merge Requests). Load this file only when the platform is GitLab.
Core workflow, scope rules, and description structure live in `SKILL.md`.

> GitLab calls PRs **Merge Requests (MRs)**. All concepts map 1:1; only CLI commands differ.

---

## Prerequisites

```bash
command -v git  >/dev/null || { echo "git is required"; exit 1; }
command -v glab >/dev/null || { echo "glab CLI required — https://gitlab.com/gitlab-org/cli"; exit 1; }
glab auth status >/dev/null 2>&1 || { echo "Not authenticated — run 'glab auth login'"; exit 1; }
git fetch origin --quiet
```

---

## Base Branch Detection

```bash
detect_base_branch() {
  local mr_base=$(glab mr view --output json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('target_branch',''))" 2>/dev/null)
  [[ -n "$mr_base" ]] && { echo "$mr_base"; return; }

  local gl_default=$(glab repo view --output json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('default_branch',''))" 2>/dev/null)
  [[ -n "$gl_default" ]] && { echo "$gl_default"; return; }

  local remote_head=$(git remote show origin 2>/dev/null | grep "HEAD branch" | cut -d: -f2 | xargs)
  [[ -n "$remote_head" ]] && { echo "$remote_head"; return; }

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
# Commits in the MR (since last push to remote branch)
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

## MR Detection & Info

```bash
# Check for open MR on current branch
glab mr view --output json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('state') == 'opened': print(d['iid'])
" 2>/dev/null

# Full MR details
glab mr view --output json
```

---

## Creating & Updating MRs

```bash
# Create new MR
glab mr create --title "Title" --description "Body" --target-branch "$BASE_BRANCH"

# Update existing MR
glab mr update --title "New Title" --description "New Body"

# Add reviewers / labels
glab mr update --reviewer username1,username2
glab mr update --label "enhancement,needs-review"
```

---

## Closing MRs

```bash
# Close (without merging) the open MR on the current branch
glab mr close

# Close a specific MR by IID
glab mr close <MR_IID>
```

---

## Viewing Changes

```bash
glab mr diff
glab mr view --output json | python3 -c "import sys,json; [print(f['new_path']) for f in json.load(sys.stdin).get('changes',[])]"
```

---

## Common Patterns

### Feature Flag
```markdown
## Feature Flag
Controlled by `FEATURE_FLAG_NAME` (default: `false`).
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
