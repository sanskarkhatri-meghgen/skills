# Meghgen Agent Skills

Reusable, version-controlled **Agent Skills** for pull-request writing and management, multi-repository architecture analysis, and autonomous test generation.

These skills are designed around the open `SKILL.md` format: each capability lives in its own folder, uses YAML frontmatter to describe when it should activate, and can bundle supporting references or scripts that the coding agent loads only when needed.

> **Platform setup verified:** July 16, 2026  
> Agent products change quickly. The platform-specific paths and commands below are based on the current Claude Code, Codex, Gemini CLI, and Cursor documentation. The Antigravity section uses the portable Agent Skills layout and includes a compatibility fallback because Antigravity builds and UI labels are changing rapidly.

---

## Table of contents

- [What is in this repository?](#what-is-in-this-repository)
- [What is an Agent Skill?](#what-is-an-agent-skill)
- [Requirements](#requirements)
- [Important folder-name compatibility note](#important-folder-name-compatibility-note)
- [Recommended portable installation](#recommended-portable-installation)
- [Claude Code setup](#claude-code-setup)
- [Antigravity setup](#antigravity-setup)
- [Codex setup](#codex-setup)
- [Gemini CLI setup](#gemini-cli-setup)
- [Cursor setup](#cursor-setup)
- [How to invoke the skills](#how-to-invoke-the-skills)
- [PR Description Writer](#1-pr-description-writer)
- [Multi-Repo Architect](#2-multi-repo-architect)
- [Autonomous Test Case Generator](#3-autonomous-test-case-generator)
- [Troubleshooting](#troubleshooting)
- [Updating the skills](#updating-the-skills)
- [Security guidance](#security-guidance)
- [Repository structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)
- [Official platform documentation](#official-platform-documentation)

---

## What is in this repository?

| Skill | Installed name | Primary purpose | Main outputs |
|---|---|---|---|
| [`pr-desc-writer/`](./pr-desc-writer/) | `pr-description-writer` | Draft, create, update, or close pull requests and merge requests from committed branch changes | `PR_DESCRIPTION.md`, PR/MR creation or management actions |
| [`multi-repo-architect/`](./multi-repo-architect/) | `multi-repo-architect` | Build a unified architecture model from one or more repositories | `architecture.md`, two Draw.io diagrams, `issues.md` |
| [`generating-test-cases/`](./generating-test-cases/) | `generating-test-cases` | Plan, generate, run, and verify test suites with coverage | Test source file and `<test-file>.report.md` |

The repository contains instructions, templates, platform-specific references, parser guidance, and one helper script. It does not ship an application, package manager, or runtime of its own.

---

## What is an Agent Skill?

An Agent Skill is a folder containing a required `SKILL.md` file and optional supporting resources:

```text
my-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

The YAML frontmatter at the top of `SKILL.md` tells an agent:

- the skill's name;
- what it does;
- when it should activate;
- and, on platforms that support it, which tools or invocation policies apply.

The Markdown body contains the workflow. Supporting files keep the entrypoint focused while allowing the agent to load detailed platform commands, parsing patterns, templates, or executable helpers only when required.

Skills normally activate in either of two ways:

1. **Implicit activation** — the agent recognizes that your request matches the skill description.
2. **Explicit activation** — you name or select the skill directly.

Because these skills can read repositories, run shell commands, write files, execute tests, or manage hosted pull requests, inspect the contents before installing them and keep approval prompts enabled for consequential actions.

---

## Requirements

### Required for all skills

- Git
- A coding agent with filesystem access
- A shell or integrated terminal
- Permission to read the target repositories
- Permission to write generated files into the working directory

### Additional requirements by skill

| Skill | Additional requirements |
|---|---|
| PR Description Writer | A configured `origin` remote; pushed source/base branches; hosting CLI or API credentials only when creating, updating, or closing a PR/MR |
| Multi-Repo Architect | Access to all repositories or archives being analyzed; Python 3 for the included Draw.io URL helper |
| Test Case Generator | The target language runtime, project dependencies, test runner, and coverage tooling |

### Hosting requirements for PR/MR actions

Drafting `PR_DESCRIPTION.md` uses Git only. Publishing or managing a hosted PR/MR needs the relevant platform tooling:

| Hosting platform | Required tooling or credentials |
|---|---|
| GitHub | `gh` CLI and `gh auth login` |
| GitLab | `glab` CLI and `glab auth login` |
| Bitbucket Cloud | `curl`, Python 3, and `BB_USER`, `BB_TOKEN`, `BB_WORKSPACE`, `BB_REPO` |
| Gitea / Forgejo | `curl`, Python 3, and `GITEA_URL`, `GITEA_TOKEN`, `GITEA_OWNER`, `GITEA_REPO` |
| Azure DevOps | Azure CLI with DevOps support plus `AZURE_ORG`, `AZURE_PROJECT`, `AZURE_REPO` |
| AWS CodeCommit | AWS CLI, configured AWS credentials, `CC_REPO`, and optionally `CC_REGION` |

---

## Important folder-name compatibility note

The repository folder is named:

```text
pr-desc-writer/
```

but its `SKILL.md` declares:

```yaml
name: pr-description-writer
```

Cursor currently requires the declared `name` to match the parent folder name. Other agents also behave more predictably when those names agree.

**Install this skill under the destination folder name `pr-description-writer`:**

```text
<skills-root>/pr-description-writer/SKILL.md
```

The source folder can remain `pr-desc-writer`; only the installed folder or symlink name needs to be changed.

The other two folders already match their declared names:

```text
multi-repo-architect/
generating-test-cases/
```

---

## Recommended portable installation

The most portable project-level location is:

```text
.agents/skills/
```

Codex, Gemini CLI, and Cursor officially discover this location. It is also the recommended shared location for Agent-Skills-capable Antigravity builds. Claude Code uses `.claude/skills/`, so mirror or symlink the same folders there.

### Option A: Unix/macOS symlink installation

Clone the source once:

```bash
git clone https://github.com/sanskarkhatri-meghgen/skills.git \
  "$HOME/.local/share/meghgen-agent-skills"
```

From the root of a project where the skills should be available:

```bash
SKILLS_SOURCE="$HOME/.local/share/meghgen-agent-skills"

mkdir -p .agents/skills .claude/skills

ln -sfn "$SKILLS_SOURCE/pr-desc-writer" \
  .agents/skills/pr-description-writer
ln -sfn "$SKILLS_SOURCE/multi-repo-architect" \
  .agents/skills/multi-repo-architect
ln -sfn "$SKILLS_SOURCE/generating-test-cases" \
  .agents/skills/generating-test-cases

ln -sfn "$(pwd)/.agents/skills/pr-description-writer" \
  .claude/skills/pr-description-writer
ln -sfn "$(pwd)/.agents/skills/multi-repo-architect" \
  .claude/skills/multi-repo-architect
ln -sfn "$(pwd)/.agents/skills/generating-test-cases" \
  .claude/skills/generating-test-cases
```

Benefits:

- one source checkout;
- references and scripts stay attached;
- updates require only `git pull`;
- the same project works in Claude Code, Codex, Gemini CLI, Cursor, and compatible Antigravity builds.

### Option B: Unix/macOS copy installation

Use this when symlinks are not desirable:

```bash
git clone https://github.com/sanskarkhatri-meghgen/skills.git \
  /tmp/meghgen-agent-skills

rm -rf .agents/skills/pr-description-writer
rm -rf .agents/skills/multi-repo-architect
rm -rf .agents/skills/generating-test-cases
rm -rf .claude/skills/pr-description-writer
rm -rf .claude/skills/multi-repo-architect
rm -rf .claude/skills/generating-test-cases

mkdir -p .agents/skills .claude/skills

cp -R /tmp/meghgen-agent-skills/pr-desc-writer \
  .agents/skills/pr-description-writer
cp -R /tmp/meghgen-agent-skills/multi-repo-architect \
  .agents/skills/multi-repo-architect
cp -R /tmp/meghgen-agent-skills/generating-test-cases \
  .agents/skills/generating-test-cases

cp -R .agents/skills/pr-description-writer .claude/skills/
cp -R .agents/skills/multi-repo-architect .claude/skills/
cp -R .agents/skills/generating-test-cases .claude/skills/
```

### Option C: Windows PowerShell project installation

```powershell
git clone https://github.com/sanskarkhatri-meghgen/skills.git `
  "$HOME\AppData\Local\meghgen-agent-skills"

$Source = "$HOME\AppData\Local\meghgen-agent-skills"

New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
New-Item -ItemType Directory -Force ".claude\skills" | Out-Null

$Names = @(
  "pr-description-writer",
  "multi-repo-architect",
  "generating-test-cases"
)

foreach ($Name in $Names) {
  Remove-Item ".agents\skills\$Name" -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item ".claude\skills\$Name" -Recurse -Force -ErrorAction SilentlyContinue
}

Copy-Item "$Source\pr-desc-writer" `
  ".agents\skills\pr-description-writer" -Recurse
Copy-Item "$Source\multi-repo-architect" `
  ".agents\skills\multi-repo-architect" -Recurse
Copy-Item "$Source\generating-test-cases" `
  ".agents\skills\generating-test-cases" -Recurse

Copy-Item ".agents\skills\pr-description-writer" `
  ".claude\skills\pr-description-writer" -Recurse
Copy-Item ".agents\skills\multi-repo-architect" `
  ".claude\skills\multi-repo-architect" -Recurse
Copy-Item ".agents\skills\generating-test-cases" `
  ".claude\skills\generating-test-cases" -Recurse
```

> Preserve each complete folder. Copying only `SKILL.md` breaks platform references and removes the Draw.io helper script.

---

## Claude Code setup

Claude Code supports project-level and personal skills.

| Scope | Location |
|---|---|
| Project | `.claude/skills/<skill-name>/SKILL.md` |
| Personal/global | `~/.claude/skills/<skill-name>/SKILL.md` |

### Project-level installation

```bash
git clone https://github.com/sanskarkhatri-meghgen/skills.git \
  "$HOME/.local/share/meghgen-agent-skills"

mkdir -p .claude/skills

ln -sfn "$HOME/.local/share/meghgen-agent-skills/pr-desc-writer" \
  .claude/skills/pr-description-writer
ln -sfn "$HOME/.local/share/meghgen-agent-skills/multi-repo-architect" \
  .claude/skills/multi-repo-architect
ln -sfn "$HOME/.local/share/meghgen-agent-skills/generating-test-cases" \
  .claude/skills/generating-test-cases
```

### Personal/global installation

```bash
mkdir -p "$HOME/.claude/skills"

ln -sfn "$HOME/.local/share/meghgen-agent-skills/pr-desc-writer" \
  "$HOME/.claude/skills/pr-description-writer"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/multi-repo-architect" \
  "$HOME/.claude/skills/multi-repo-architect"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/generating-test-cases" \
  "$HOME/.claude/skills/generating-test-cases"
```

### Verify in Claude Code

Start Claude Code in a Git repository:

```bash
claude
```

Invoke a skill directly:

```text
/pr-description-writer
/multi-repo-architect
/generating-test-cases
```

Claude may also activate a skill automatically when your request matches its description.

Claude Code derives the slash command from the installed directory name, not from the source repository folder. This is another reason to install the PR skill as `pr-description-writer`.

### Reload behavior

Claude Code watches existing skill directories for changes. Edits to a skill normally appear during the current session. When the top-level `.claude/skills/` directory did not exist at session startup and is created afterward, restart Claude Code so it can begin watching that directory.

---

## Antigravity setup

Antigravity has changed quickly across preview and 2.x builds. Use the portable Agent Skills layout first, then use the product's Skills or Customization interface as a fallback when a specific build does not automatically discover the directory.

### Recommended project-level layout

```text
your-project/
└── .agents/
    └── skills/
        ├── pr-description-writer/
        │   ├── SKILL.md
        │   └── references/
        ├── multi-repo-architect/
        │   ├── SKILL.md
        │   ├── references/
        │   └── scripts/
        └── generating-test-cases/
            └── SKILL.md
```

Install using the [recommended portable installation](#recommended-portable-installation), then reopen or refresh the workspace.

### Recommended global layout

For builds that support global Agent Skills discovery:

```text
~/.agents/skills/
```

Install the same three complete folders there.

### Verify in Antigravity

Ask without executing anything:

```text
List the Agent Skills available in this workspace. Show each skill's name and description only.
```

Then explicitly name the skill in a task:

```text
Use the pr-description-writer skill to draft a PR description for this branch.
```

```text
Use the multi-repo-architect skill. Analyze these repositories and generate architecture.md and issues.md.
```

```text
Use the generating-test-cases skill to plan unit tests for the selected function.
```

### Compatibility fallback

When the installed Antigravity build does not enumerate `.agents/skills/` automatically:

1. Open the product's Skills, Agent Skills, or Customization surface.
2. Add or link the folder containing the three installed skill directories.
3. Restart or refresh the workspace.
4. Ask it to list available skills again.
5. If native skill linking is absent, add a workspace instruction that tells the agent to read the matching `.agents/skills/<name>/SKILL.md` before performing one of these workflows.

Project-local installation is preferable for Antigravity because it keeps the instructions versioned with the codebase and avoids relying on changing global configuration paths.

---

## Codex setup

Codex discovers skills from `.agents/skills` at repository and user scope.

| Scope | Location |
|---|---|
| Current/repository hierarchy | `.agents/skills/<skill-name>/SKILL.md` |
| Personal/global | `~/.agents/skills/<skill-name>/SKILL.md` |
| Admin/system | `/etc/codex/skills/<skill-name>/SKILL.md` |

Codex scans `.agents/skills` from the current working directory upward to the repository root. This allows root-wide skills and component-specific skills in nested directories.

### Project-level installation

Use the portable installation so the project contains:

```text
.agents/skills/pr-description-writer/SKILL.md
.agents/skills/multi-repo-architect/SKILL.md
.agents/skills/generating-test-cases/SKILL.md
```

### Personal/global installation

```bash
git clone https://github.com/sanskarkhatri-meghgen/skills.git \
  "$HOME/.local/share/meghgen-agent-skills"

mkdir -p "$HOME/.agents/skills"

ln -sfn "$HOME/.local/share/meghgen-agent-skills/pr-desc-writer" \
  "$HOME/.agents/skills/pr-description-writer"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/multi-repo-architect" \
  "$HOME/.agents/skills/multi-repo-architect"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/generating-test-cases" \
  "$HOME/.agents/skills/generating-test-cases"
```

### Verify and invoke in Codex

Open the skill selector:

```text
/skills
```

Explicitly mention a skill by typing `$` and selecting it, or by entering:

```text
$pr-description-writer
$multi-repo-architect
$generating-test-cases
```

Codex can also activate a skill implicitly when the request matches its `description`.

### Optional built-in installer

Codex includes a `$skill-installer`. You can ask it to install the three skill folders from this repository, but the manual or symlink installation is more predictable for this multi-skill repository because it lets you apply the required `pr-description-writer` destination name.

Example installer request:

```text
$skill-installer Install all three Agent Skills from
https://github.com/sanskarkhatri-meghgen/skills.
Preserve every references and scripts directory.
Install pr-desc-writer under the folder name pr-description-writer.
```

Codex detects most skill changes automatically. Restart Codex if a newly installed skill does not appear.

---

## Gemini CLI setup

Gemini CLI supports both Gemini-specific and portable Agent Skills directories.

| Scope | Primary location | Portable alias |
|---|---|---|
| Workspace/project | `.gemini/skills/` | `.agents/skills/` |
| User/global | `~/.gemini/skills/` | `~/.agents/skills/` |

Within the same tier, Gemini CLI gives `.agents/skills/` precedence over `.gemini/skills/`. Using `.agents/skills/` avoids maintaining another duplicate for Codex and Cursor.

### Manual project installation

Use the portable setup and confirm these paths exist:

```text
.agents/skills/pr-description-writer/SKILL.md
.agents/skills/multi-repo-architect/SKILL.md
.agents/skills/generating-test-cases/SKILL.md
```

### Install from the Gemini CLI

Gemini CLI can install a skill from a Git repository and a selected subdirectory:

```bash
gemini skills install \
  https://github.com/sanskarkhatri-meghgen/skills.git \
  --path multi-repo-architect \
  --scope user
```

```bash
gemini skills install \
  https://github.com/sanskarkhatri-meghgen/skills.git \
  --path generating-test-cases \
  --scope user
```

For the PR skill, manual installation is recommended so the destination folder can be named `pr-description-writer`. When using the installer, inspect the installed folder afterward and rename it if it remains `pr-desc-writer`.

Use `--consent` only when you have reviewed the skill and intentionally want to bypass the install confirmation:

```bash
gemini skills install \
  https://github.com/sanskarkhatri-meghgen/skills.git \
  --path multi-repo-architect \
  --scope workspace \
  --consent
```

### Verify and manage skills

From the terminal:

```bash
gemini skills list --all
```

Inside an interactive Gemini CLI session:

```text
/skills list
/skills reload
```

Other management commands include:

```text
/skills disable <name>
/skills enable <name>
/skills link <path> --scope user
/skills link <path> --scope workspace
```

Gemini CLI activates a skill through its `activate_skill` flow and asks for consent before adding the skill body and directory resources to the active conversation.

To explicitly steer activation, write:

```text
Use the multi-repo-architect skill for this task.
```

---

## Cursor setup

Cursor officially discovers skills from the following locations:

| Scope | Locations |
|---|---|
| Project | `.agents/skills/`, `.cursor/skills/` |
| User/global | `~/.agents/skills/`, `~/.cursor/skills/` |

Cursor also loads compatible skills from Claude and Codex directories, including `.claude/skills/` and `.codex/skills/`, but `.agents/skills/` is the cleanest shared project layout.

### Project-level installation

Use the portable setup:

```text
.agents/skills/pr-description-writer/SKILL.md
.agents/skills/multi-repo-architect/SKILL.md
.agents/skills/generating-test-cases/SKILL.md
```

Cursor recursively discovers nested skills and can scope skills placed inside a monorepo package to that package's files.

### Personal/global installation

```bash
mkdir -p "$HOME/.cursor/skills"

ln -sfn "$HOME/.local/share/meghgen-agent-skills/pr-desc-writer" \
  "$HOME/.cursor/skills/pr-description-writer"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/multi-repo-architect" \
  "$HOME/.cursor/skills/multi-repo-architect"
ln -sfn "$HOME/.local/share/meghgen-agent-skills/generating-test-cases" \
  "$HOME/.cursor/skills/generating-test-cases"
```

### Import through the Cursor UI

Cursor can import remote rules or skills from GitHub:

1. Open **Customize**.
2. Go to **Rules**.
3. Select **Add Rule**.
4. Choose **Remote Rule (GitHub)**.
5. Enter this repository's URL.

For this repository, filesystem installation is more predictable because it preserves all three independent skill folders and applies the PR folder-name compatibility fix.

### Verify and invoke in Cursor

Open **Customize → Skills** to inspect discovered skills.

In Agent chat, type `/` and select:

```text
/pr-description-writer
/multi-repo-architect
/generating-test-cases
```

Cursor may also invoke a skill automatically when the task matches its description.

---

## How to invoke the skills

### Platform invocation summary

| Platform | Explicit invocation |
|---|---|
| Claude Code | `/pr-description-writer`, `/multi-repo-architect`, `/generating-test-cases` |
| Antigravity | State `Use the <skill-name> skill...` or select it in the available Skills surface |
| Codex | Mention `$pr-description-writer`, `$multi-repo-architect`, or `$generating-test-cases`; `/skills` opens the selector |
| Gemini CLI | State `Use the <skill-name> skill...`; Gemini requests activation consent |
| Cursor | `/pr-description-writer`, `/multi-repo-architect`, `/generating-test-cases` |

### Natural-language activation

All three skills have detailed descriptions intended to support automatic activation. Explicit naming is still recommended when:

- more than one skill could apply;
- the agent did not activate the expected skill;
- you are testing installation;
- or the request could have consequential side effects.

---

# 1. PR Description Writer

**Source:** [`pr-desc-writer/`](./pr-desc-writer/)  
**Installed name:** `pr-description-writer`

## What it does

The PR Description Writer creates concise, reviewer-friendly PR or MR descriptions based on the **committed, pushed diff** between a source branch and a base branch.

It also supports explicit hosting-platform actions:

- create/open a PR or MR;
- update an existing title or description;
- add reviewers or labels where supported;
- close, abandon, or decline a PR/MR;
- target a branch that is not currently checked out;
- work across GitHub, GitLab, Bitbucket, Gitea/Forgejo, Azure DevOps, and AWS CodeCommit.

## Core safety and scope rules

The skill treats the remote branch state as the source of truth:

```text
origin/BASE_BRANCH...origin/SOURCE_BRANCH
```

It deliberately excludes:

- staged changes;
- unstaged changes;
- uncommitted files;
- unpushed commits;
- and the current working tree as architectural context.

Important behavior:

- It runs `git fetch origin` before analysis.
- It does not hardcode `main` or `master`.
- It can infer stacked branch relationships through merge-base ancestry.
- It asks you to confirm or override an inferred base branch.
- It validates that source and base share history.
- It detects a reversed comparison where the source is behind the base.
- It never switches the locally checked-out branch.
- It reads committed context with `git show`, `git ls-tree`, and `git grep`.
- It never runs or imports repository code while drafting.
- It does not publish anything unless the user explicitly asks.
- It warns when local commits are unpushed and therefore excluded.
- It notes uncommitted changes without including them.
- It detects the hosting platform only when a hosted action is actually required.

## Two operating modes

### Generation Mode

Generation Mode is the default for requests such as:

```text
Write a PR description.
```

Workflow:

1. Fetch remote refs.
2. Resolve the source branch.
3. Infer or accept the base branch.
4. Ask for confirmation when the base was inferred.
5. Validate ancestry and direction.
6. Inspect commits, diff statistics, full diff, and committed architectural context.
7. Review commit messages.
8. Generate the fixed PR description structure.
9. Write or overwrite `PR_DESCRIPTION.md`, unless another path was requested.
10. Report the output path.
11. Ask whether to open the PR/MR.
12. Detect the platform and publish only after explicit confirmation.

### Direct-Action Mode

Direct-Action Mode activates when the prompt already contains the exact title/body or asks for a hosted PR action.

Examples:

```text
Open a PR titled "Fix token refresh" with description "Handles expired access tokens."
```

```text
Update my PR description to "Adds retry handling and tests."
```

```text
Close the PR for branch feature/old-flow.
```

In Direct-Action Mode the skill:

- fetches remote refs;
- resolves and validates branches for create actions;
- skips diff analysis when an exact inline body was supplied;
- detects the hosting platform immediately before acting;
- locates the open PR/MR;
- creates, edits, closes, or manages it;
- and does not write `PR_DESCRIPTION.md` unless a local copy was also requested.

When a create request omits an inline body, it looks for `PR_DESCRIPTION.md`. If none exists, it asks for a description.

## Generated PR description format

The section order is fixed:

```markdown
## Summary

## Rationale

## Changes
| Change | Detail |
|---|---|

## How to Test

## Notes
```

Rules:

- **Summary** is always present and explains what changed.
- **Rationale** is always present and explains why. When the reason is absent from the diff and commits, it says so instead of inventing one.
- **Changes** is always a table with one row per atomic change.
- Change rows follow diff-stat order for deterministic output.
- **How to Test** is included only when there is something meaningful to test.
- Automated commands come before manual test steps.
- **Notes** appears only for reviewer-relevant surprises such as migrations, breaking changes, environment variables, deploy steps, limitations, or follow-ups.
- ASCII or Mermaid diagrams are added only for genuinely complex flows, decision trees, pipelines, or state machines.

## Existing-PR behavior

Before creating a PR/MR, the skill checks whether an open one already exists for the source branch.

When one exists, it asks whether to update the current PR/MR rather than create a duplicate. Closed and merged requests are not treated as active targets.

## Phrase cookbook

### Drafting and summarizing

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Draft from the current branch | `Write a PR description for my changes.` | Analyzes pushed commits, confirms base when needed, writes `PR_DESCRIPTION.md` |
| Use review-oriented wording | `Prepare my branch for review.` | Same Generation Mode workflow |
| Ask what the PR should say | `What should my PR say?` | Builds the fixed Summary/Rationale/Changes format |
| Summarize all pushed changes | `Describe the changes on this branch for a PR.` | Covers the entire base-to-source range, not only the latest commit |
| Specify both branches | `Write a PR description for merging feature/auth into develop.` | Uses the named source and base without switching checkout |
| Describe another source branch | `Draft the PR for branch-one against main while I remain on branch-two.` | Reads `origin/branch-one` directly and leaves checkout untouched |
| Choose a custom output | `Write the PR description to docs/auth-pr.md.` | Writes to the requested file instead of the default |
| Include unpushed work | `Include my latest local commit.` | Warns that unpushed commits are excluded and asks you to push first |
| Regenerate after pushing | `Regenerate the PR description now that I pushed.` | Fetches and recalculates from the latest remote source branch |

### Creating and publishing

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Draft, then open | `Write the PR description and then ask me before opening it.` | Generates locally, then waits for explicit confirmation |
| Open after reviewing the draft | `Yes, open the PR now.` | Detects platform, checks for an existing open PR, then creates or updates |
| Create with exact body | `Open a PR titled "Fix auth" with description "Refreshes expired tokens."` | Direct-Action Mode; preserves quoted body exactly |
| Create from a file | `Create the PR using PR_DESCRIPTION.md.` | Reads the provided body and performs the hosted action |
| Create for named branches | `Open a PR to merge feature/payments into release with description "Adds payment retries."` | Uses the named branches without checking them out |
| Keep a local copy too | `Open the PR with this body and also save it to PR_DESCRIPTION.md.` | Performs direct action and writes the requested local copy |

### Updating metadata

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Replace description | `Update my PR description to "Adds retries and timeout handling."` | Targets the open PR for the current branch unless another target is named |
| Replace title | `Change the PR title to "Harden payment retries".` | Updates only the title |
| Target a different branch | `Update the PR for feature/payments with this description: "..."` | Finds the PR for the named branch |
| Add reviewers | `Add reviewers alice and bob to this PR.` | Uses the platform-specific reviewer action where available |
| Add labels | `Add labels enhancement and needs-review.` | Applies labels on platforms that support the reference action |
| Add both | `Add reviewer alice and label security to the current PR.` | Applies both requested metadata changes |

### Closing

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Close current PR | `Close the PR for this branch.` | Finds the current branch's open PR and closes it without merging |
| Close by number | `Close PR #42.` | Targets the specified PR where the platform supports numeric IDs |
| GitLab wording | `Close the current merge request.` | Uses GitLab MR commands |
| Bitbucket wording | `Decline pull request 17.` | Uses Bitbucket's decline endpoint |
| Azure wording | `Abandon the active PR for feature/legacy.` | Sets the Azure DevOps PR to abandoned |
| Named non-current branch | `Close the PR for branch-two without switching branches.` | Locates that branch's PR and preserves local checkout |

### Base-branch and stacked-branch control

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Accept inferred parent | `Use the nearest parent branch as the base.` | Uses merge-base ancestry result |
| Override candidate | `Use main as the base instead of branch-one.` | Validates the override before diffing |
| Correct direction | `I meant to merge main into feature/auth.` | Re-evaluates the source/base direction |
| Stop duplicate creation | `Update the existing PR instead.` | Switches from create to update when a PR already exists |

## Platform-specific actions

### GitHub

Supports:

- PR detection and details;
- creation;
- title/body updates;
- reviewers;
- labels;
- closing;
- viewing diffs, files, and commits.

Authentication check:

```bash
gh auth status
```

### GitLab

Uses Merge Request terminology and supports:

- MR detection;
- creation;
- title/body updates;
- reviewers;
- labels;
- closing;
- diff inspection.

Authentication check:

```bash
glab auth status
```

### Bitbucket Cloud

Uses REST APIs for:

- open PR detection;
- creation;
- updates;
- decline/close.

Required environment variables:

```text
BB_USER
BB_TOKEN
BB_WORKSPACE
BB_REPO
```

### Gitea / Forgejo

Uses the Gitea-compatible REST API for:

- open PR detection;
- creation;
- title/body updates;
- closing.

Required environment variables:

```text
GITEA_URL
GITEA_TOKEN
GITEA_OWNER
GITEA_REPO
```

### Azure DevOps

Supports:

- active PR detection;
- creation;
- title/body update;
- adding reviewers;
- abandoning a PR.

Required environment variables:

```text
AZURE_ORG
AZURE_PROJECT
AZURE_REPO
```

### AWS CodeCommit

Supports:

- open pull request discovery;
- creation;
- title update;
- description update;
- closing.

Required environment variables:

```text
CC_REPO
CC_REGION
```

`CC_REGION` falls back to the configured AWS CLI region.

## What this skill intentionally does not do

- It does not include working-tree changes in a generated description.
- It does not silently publish a generated draft.
- It does not switch branches.
- It does not assume the default branch is `main`.
- It does not execute application code or tests while drafting.
- It does not invent a rationale absent from commits and diff context.
- It does not create duplicate open PRs without warning.
- It does not add diagrams to simple changes merely for decoration.

---

# 2. Multi-Repo Architect

**Source and installed name:** [`multi-repo-architect/`](./multi-repo-architect/)

## What it does

Multi-Repo Architect statically analyzes one or more repositories and builds a unified model of the complete system.

It is intended for combinations such as:

- frontend and backend repositories;
- multiple backend services;
- application and Terraform repositories;
- Docker Compose environments;
- Kubernetes or Helm configuration;
- gateways and proxies;
- CI/CD repositories;
- deployment configuration;
- monorepos containing several co-located components.

It can also analyze a single repository when architecture analysis, architecture diagrams, or system-wide issue detection is explicitly requested.

## First interaction: choose deliverables

The skill begins by asking which outputs you want:

1. `architecture.md`
2. `low-level-diagram.drawio`
3. `high-level-diagram.drawio`
4. `issues.md`

Request multiple outputs or say **all four** when you want the complete set.

This explicit request resolves legacy wording later in the skill that refers to generating all files. The top-level behavior is to generate the deliverables you selected.

## Accepted repository inputs

The skill can combine input forms in the same request:

### Uploaded archives

```text
frontend.zip
backend.zip
infrastructure.zip
```

### Local paths

```text
/workspaces/frontend
/workspaces/backend
/workspaces/platform
```

### GitHub or GitLab URLs

```text
https://github.com/example/frontend
https://gitlab.com/example/backend
```

Private repository access may require a token or an already authenticated local checkout.

When only one repository is supplied, the skill asks whether related repositories should be included before it proceeds.

## Component discovery

The skill classifies **components**, not just whole repositories. This matters for monorepos and directories that combine application and infrastructure code.

A component boundary is inferred from concrete files:

| Boundary signal | Inferred role |
|---|---|
| React/Vue/Angular dependencies, or frontend `index.html` structure | Frontend |
| Express/Fastify `package.json`, `go.mod`, `requirements.txt`, `pom.xml`, `main.go`, `app.py` | Backend service |
| `*.tf`, especially `main.tf` | Terraform infrastructure |
| `docker-compose.yml` or `.yaml` | Orchestration |
| `Dockerfile` without a stronger app boundary | Containerized service |
| `k8s/`, `kubernetes/`, `manifests/`, `helm/` | Kubernetes |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` | CI/CD |
| `nginx.conf`, `traefik.yml`, `haproxy.cfg` | Gateway or proxy |

When multiple boundary signals occur in the same directory, the skill keeps them as one combined component instead of inventing artificial boundaries.

It announces the discovered components and inferred roles before deep parsing. It pauses only when classification is genuinely ambiguous.

## Language and framework parsing

### Node.js, JavaScript, and TypeScript

Reads high-signal files such as:

- `package.json`;
- application entrypoints;
- route/API directories;
- environment examples;
- Docker Compose files.

Looks for:

- Express, Fastify, NestJS, frontend frameworks, and build tooling;
- HTTP route definitions;
- outbound HTTP clients;
- Redis clients;
- SQL and NoSQL connectors;
- AWS SDK usage;
- RabbitMQ and Kafka clients.

### Python

Reads:

- `requirements.txt`, `pyproject.toml`, or `Pipfile`;
- `main.py`, `app.py`, `wsgi.py`, or `asgi.py`;
- route/view/API directories;
- settings and environment files.

Recognizes patterns for:

- Flask;
- FastAPI;
- Django;
- Celery;
- HTTP clients;
- PostgreSQL and SQLAlchemy;
- MongoDB;
- Redis;
- AWS SDK;
- RabbitMQ and Kafka.

### Go

Reads:

- `go.mod`;
- `main.go` and `cmd/*/main.go`;
- server, API, handler, and config directories.

Recognizes:

- Gin;
- Echo;
- Gorilla Mux;
- Chi;
- gRPC;
- HTTP clients;
- database libraries;
- Redis;
- AWS SDK usage.

### Java and Kotlin

Focuses on Spring Boot conventions:

- Maven or Gradle manifests;
- application classes;
- controllers;
- `application.yml` and properties files;
- REST mappings;
- Feign, WebClient, and RestTemplate;
- JPA;
- Kafka;
- Redis.

### Rust

Reads Cargo manifests, entrypoints, routes, and handlers. Recognizes common web frameworks including:

- Actix Web;
- Axum;
- Warp;
- Rocket.

### Unknown or unlisted technologies

The parser lists are starting points, not hard limits. The skill is instructed to investigate unfamiliar technologies such as:

- Pulumi;
- Dagger;
- Bazel;
- serverless frameworks;
- Airflow or Prefect;
- ML frameworks;
- and other infrastructure, build, or data systems.

It should not omit a component merely because its technology is absent from the reference tables.

## Infrastructure parsing

### Terraform

Extracts:

- providers and regions;
- input variables;
- outputs;
- modules;
- state backends;
- networking;
- compute;
- databases;
- storage;
- queues and topics;
- IAM policies;
- load balancers;
- DNS and CDN resources.

It recognizes AWS, GCP, and Azure resource patterns and checks for risk signals such as:

- public database access;
- sensitive ports open to `0.0.0.0/0`;
- public S3 ACLs;
- wildcard IAM actions/resources;
- missing Multi-AZ;
- missing deletion protection;
- oversized development instances.

### Docker and Docker Compose

Extracts:

- service names;
- build or image source;
- exposed ports;
- environment values;
- service URLs;
- `depends_on`;
- health checks;
- networks;
- volumes;
- replicas;
- resource limits.

It also flags mutable `:latest` image tags and hardcoded secrets where visible.

### Kubernetes and Helm

Extracts:

- Deployments and StatefulSets;
- replicas;
- images;
- resource requests and limits;
- readiness and liveness probes;
- ConfigMaps and Secrets;
- Services and service types;
- Ingress hosts, paths, TLS, and backend routing;
- namespaces.

### CI/CD

Extracts:

- triggers;
- test, lint, and build steps;
- image publishing;
- deployment commands;
- target environments;
- deployment strategy.

## Unified system model

The skill builds an internal model containing:

- services and their roles;
- repositories and component paths;
- languages and frameworks;
- exposed protocols, ports, and routes;
- service-to-service calls;
- databases;
- caches;
- queues and topics;
- external APIs;
- environment variables;
- containers and images;
- cloud provider, region, networking, compute, and managed services;
- ingress points;
- CI/CD and deployment strategy.

### Connection resolution

Environment variables are treated as a major dependency interface.

Examples:

```text
USER_SERVICE_URL=http://users:8080
DATABASE_URL=postgres://...
REDIS_HOST=redis
ORDER_TOPIC_ARN=...
```

When a value maps directly to a discovered service, database, queue, or topic, the connection is marked **confirmed**.

When only a variable name or unresolved template implies a connection, it is marked **inferred**.

Unknowns remain explicitly unknown instead of being filled with invented architecture.

## Deliverable 1: `architecture.md`

The architecture document includes:

1. System overview
2. Technology stack summary
3. One section per service
4. Data architecture and data flow
5. Infrastructure and networking
6. Compute resources
7. Load balancing, ingress, DNS, and CDN
8. Synchronous service communication
9. Asynchronous events and queues
10. Deployment and CI/CD
11. External dependencies
12. Confidence notes distinguishing confirmed, inferred, and unknown facts

## Deliverable 2: `low-level-diagram.drawio`

The low-level diagram is a logical service map showing:

- frontends;
- backend services;
- gateways;
- workers and schedulers;
- databases and caches;
- queues and topics;
- external services;
- direction of calls and event flow.

It uses relevant provider or product logos whenever possible and falls back to labeled geometric shapes only when no suitable icon exists.

## Deliverable 3: `high-level-diagram.drawio`

The high-level diagram focuses on physical/cloud topology:

- VPCs or networks;
- public and private boundaries;
- subnets;
- gateways;
- load balancers;
- clusters;
- compute;
- managed databases;
- storage;
- messaging;
- external SaaS integrations.

It uses AWS, GCP, Azure, Kubernetes, Docker, Redis, and other recognizable vendor icons where available.

## Editable Draw.io links

After generating each `.drawio` file, the skill creates a direct editable `app.diagrams.net` URL with:

```bash
python3 <skill-root>/scripts/gen_drawio_url.py \
  low-level-diagram.drawio --auto
```

```bash
python3 <skill-root>/scripts/gen_drawio_url.py \
  high-level-diagram.drawio --auto
```

The helper:

- URI-encodes the XML;
- raw-deflate compresses it with one compressor instance;
- Base64-encodes the compressed content;
- detects GCP and AWS library requirements;
- adds libraries such as `gcp2` or `aws4` to the URL.

## Deliverable 4: `issues.md`

The issues report groups findings by severity:

- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🔵 Low

Each issue contains:

- category;
- affected component;
- description;
- concrete file/config evidence;
- recommendation.

### Security categories

Examples include:

- committed secrets;
- unauthenticated routes;
- overly open security groups;
- public databases or buckets;
- permissive IAM;
- missing TLS;
- insecure CORS;
- missing rate limiting;
- insecure deserialization;
- unencrypted data;
- deprecated vulnerable dependencies;
- missing audit logging.

### Reliability categories

Examples include:

- missing health checks;
- single replicas for critical services;
- missing retry or circuit breakers;
- missing Kubernetes resource limits;
- missing connection pools;
- synchronous cascading-failure chains;
- mutable image tags;
- missing backups;
- missing readiness or liveness probes.

### Cost categories

Examples include:

- oversized instances;
- missing autoscaling;
- unused resources;
- cross-AZ transfer in hot paths;
- inefficient managed-service sizing.

The lists are intentionally non-exhaustive. The skill is expected to report technology-specific issues it discovers even when they are not in a predefined checklist.

## Interactive architecture Q&A

After generating outputs, continue using the same conversation to ask questions such as:

```text
What calls the payments service?
```

```text
Which services have no health checks?
```

```text
What would break if Redis went down?
```

```text
Trace a user login request from ingress to database.
```

```text
Which connections are confirmed and which are inferred?
```

Answers should name services, repositories, files, and line numbers where available.

## Phrase cookbook

### Selecting inputs and outputs

| Goal | Example phrases | Expected behavior |
|---|---|---|
| Full system package | `Use the multi-repo-architect skill. Analyze these repos and generate all four deliverables.` | Produces architecture, both diagrams, and issues report |
| Narrative only | `Analyze these repositories and generate architecture.md only.` | Produces the architecture document |
| Logical diagram | `Create a low-level service map for these repos.` | Produces `low-level-diagram.drawio` and editable link |
| Cloud topology | `Create a high-level cloud architecture diagram.` | Produces `high-level-diagram.drawio` and editable link |
| Risk audit | `Audit these repos for security, reliability, and cost issues and write issues.md.` | Produces severity-ranked findings |
| Selected combination | `Generate architecture.md, the low-level diagram, and issues.md.` | Produces only the requested set |
| Mixed input types | `Analyze this backend zip, this frontend path, and this Terraform GitHub repo.` | Combines all sources into one model |
| Single repo | `Analyze the architecture of this monorepo and identify system-wide issues.` | Activates despite having only one repository |

### Component and dependency analysis

| Goal | Example phrases |
|---|---|
| Discover monorepo boundaries | `Map every logical component in this monorepo before analyzing it.` |
| Explain service wiring | `Explain how the frontend, API, workers, queues, and databases connect.` |
| Resolve environment links | `Match service URL environment variables to the services they reference.` |
| Trace data | `Trace order data from the frontend through services, queues, and storage.` |
| Understand infrastructure | `Explain which Terraform resources run each application component.` |
| Explain deployment | `Map the CI/CD path from pull request to production.` |
| Find ingress | `List every public ingress point, hostname, TLS setting, and backend.` |
| Separate confidence | `Mark every architecture relationship as confirmed, inferred, or unknown.` |

### Risk-focused requests

| Goal | Example phrases |
|---|---|
| Security | `Find hardcoded secrets, public resources, permissive IAM, and unauthenticated routes.` |
| Reliability | `Find single points of failure, missing probes, missing retries, and resource-limit gaps.` |
| Cost | `Find oversized infrastructure, missing autoscaling, unused resources, and expensive data paths.` |
| Kubernetes | `Audit replicas, probes, resource requests/limits, image tags, and ingress TLS.` |
| Terraform | `Audit security groups, public databases, bucket ACLs, IAM wildcards, and stateful protections.` |
| Docker Compose | `Find services without health checks, pinned versions, limits, or persistent volumes.` |

### Follow-up questions

```text
What happens if the users service is unavailable?
```

```text
Which backend owns each database?
```

```text
Where is authentication enforced?
```

```text
Which services publish or consume order events?
```

```text
What is the highest-risk production issue and why?
```

```text
Which diagram edges were inferred rather than confirmed?
```

## What this skill intentionally does not do

- It does not invent services that are absent from code or configuration.
- It does not treat an entire monorepo as one component when boundary signals show otherwise.
- It does not assume an unresolved environment variable is a confirmed connection.
- It does not restrict analysis to the technologies listed in the parser reference.
- It does not use plain boxes when an appropriate provider icon is available.
- It does not hide uncertainty.
- It does not execute repository code as part of static architecture discovery.
- It does not silently choose all deliverables; request the required set explicitly.

---

# 3. Test Case Generator

## Overview

Generates, executes, and verifies complete test suites for any function or feature. Given a target, it autonomously discovers your project's architecture, drafts a test plan for your approval, writes the suite, runs it, and self-corrects until coverage targets are met — all without touching your source code.

---

## When to Use This Skill

### In-Scope Requests
- "Write tests for `calculate_discount()`"
- "Generate a test suite for the auth module"
- "Hit 90% coverage on `parser.py`"
- "Add edge case tests for the payment flow"

### Out-of-Scope Requests
- Debugging existing tests
- Explaining what a function does
- Refactoring source code

If the request is ambiguous, the skill will ask: *"Do you want me to generate new test cases for this, or do you need help with something else?"*

---

## Execution Modes

### Unit Mode
Activated when a specific function or method is targeted. Isolates the unit under test and mocks all external dependencies.

### Integration / Feature Mode
Activated when a feature, workflow, or whole module is targeted. Traces cross-file references, matches infrastructure patterns, and verifies combined multi-component behaviour.

The skill selects the correct mode automatically based on your request.

---

## Workflow

This skill runs as a mandatory two-stage workflow. No code is written until you approve the plan.

### Stage 1 — Discovery & Plan

1. Scans manifests and the existing test layout to detect language, framework, and conventions
2. Selects Unit or Integration / Feature Mode
3. Isolates the target function, class, or module
4. Identifies happy paths, structural boundaries, and mathematical/combinatorial test matrices
5. Presents a structured test plan with concrete inputs and expected outcomes
6. **Pauses for your approval — nothing is written to disk until you confirm**

The plan includes: discovered architecture, target mode, component branch map, representative examples with expected outcomes, MC/DC or pairwise strategy where applicable, total planned test count, and target coverage.

**What counts as approval:**
```text
Proceed.
```
```text
Looks good, go ahead.
```
```text
Approved — generate and run the tests.
```

A question, a requested change, or an additional edge case is **not** treated as approval. The skill incorporates the feedback, re-presents the updated plan, and pauses again.

### Stage 2 — Generation & Verification

1. Incorporates any plan changes you requested
2. Writes the complete test suite to disk
3. Runs the native test command and records pass / fail / skip counts
4. Runs the coverage tool
5. Appends new tests if coverage is below target — up to **3 iterations total**
6. Writes the full execution report file
7. Prints a concise summary in chat

---

## Supported Languages & Frameworks

| Language | Framework |
|----------|-----------|
| Python | pytest |
| JavaScript / TypeScript | Jest / Vitest |
| Java | JUnit 5 |
| Go | `testing` (stdlib) |
| C++ | Google Test |
| Rust | `cargo test` |
| .NET / C# | xUnit |
| Ruby | RSpec |
| PHP | PHPUnit |

Other ecosystems are supported — the skill selects the de-facto standard for whatever it detects.

---

## What the Skill Enforces Automatically

Every generated test suite is guaranteed to comply with the following, with no extra configuration required:

- **AAA Pattern** — every test is structured into Arrange, Act, and Assert blocks with comments
- **Naming Convention** — every test name encodes the unit under test, the condition, and the expected outcome, in the idiomatic style of the detected language
- **MC/DC Coverage** — boolean logic is covered using Modified Condition/Decision Coverage, not brute-force permutations
- **Parameterized Testing** — repeated cases are collapsed into parameterized matrices, not copy-pasted blocks
- **I/O Mocking** — all external boundaries (network, disk, DB, APIs) are mocked using the framework's native mocking library; no real I/O is executed
- **State Teardown** — any global state or DB mutations are rolled back after every test
- **Async Handling** — asynchronous code is handled with the correct event loop and synchronisation primitives
- **Determinism** — system clocks and random number generators are frozen where used
- **Public Interface Only** — private methods are never tested directly; only their effects through public callers
- **Assertion Precision** — all assertions target exact values, specific error types, and precise state changes
- **Source Immutability** — your source code is never modified

---

## Naming Conventions

Every test name encodes three things: the unit under test, the condition, and the expected outcome — in the idiomatic style of the detected language.

```text
# Python / pytest / Go
test_sort_when_input_empty_returns_empty
```
```text
// Java / JUnit 5
sortReturnsEmpty_whenInputIsEmpty
```
```text
// JavaScript / TypeScript (Jest / Vitest)
it('returns empty array when input is empty', ...)
```
```text
// C++ / Google Test
TEST(SortSuite, ReturnsEmptyWhenInputIsEmpty)
```

---

## Configuration

### Coverage Target
Default target is **85%**. To set a custom target, state it in your prompt:

> "Generate tests for `utils.py` with 95% coverage."

### Custom Overrides (`.test-agent-config.md`)
Place a `.test-agent-config.md` file at your workspace root to define project-specific rules — legacy fixture maps, custom mathematical constraints, or framework preferences. The skill reads this silently before planning and applies your overrides automatically.

---

## Output Contract

### Test File
Saved alongside your source using the ecosystem's standard naming convention:

| Language | Output Filename |
|----------|----------------|
| Python | `test_<source_filename>.py` |
| Go | `<source_filename>_test.go` |
| Java | `<ClassName>Test.java` under `src/test/java/...` |
| JS / TS | `<name>.test.js` / `<name>.spec.ts` |

### Execution Report
A detailed `<test_file_basename>.report.md` is written alongside the test file. Contains the full test-by-test results table, coverage breakdown, and missed lines justification. This is the complete record — not printed in full to chat.

### Chat Summary
A short summary is printed in chat once execution completes:
- Pass / fail / skip counts
- Final coverage percentage and iterations used
- Path to the full report file
- Brief notes on any failing tests (only if applicable)

### Exception Block
If execution cannot reach the final stage, the skill emits a structured halt block containing the one-line reason, the technical cause, and the required action to unblock.

---

## Limitations

- **3-iteration cap** on the self-correction loop. If coverage target is not met after 3 runs, the skill stops and documents why in the report.
- **No source modification** — if the source code has structural issues preventing testability, the skill will flag this but will not refactor it.
- **Genuinely unreachable lines** (e.g., `if __name__ == '__main__':` blocks, hardware-specific guards) are documented as *Measurement Artifacts* and excluded from the coverage calculation rather than counted as misses.
- The approval gate at Step 2 is mandatory and cannot be skipped.

---

## Phrase Cookbook

### Unit tests

| Goal | Example prompt |
|------|----------------|
| Basic unit suite | `Generate tests for calculate_total in src/billing.py` |
| Target a specific function | `Generate tests for parse_token in src/auth/token.py` |
| Let agent infer target | `Generate tests for the function in my currently selected file` |
| Error and validation paths | `Test all error and validation paths for create_user` |
| Async function | `Generate tests for this async retry function, including timeout behavior` |
| Boundary-heavy function | `Test null, empty, minimum, maximum, overflow, and malformed inputs` |
| Match existing style | `Match the repository's current fixtures, naming, and mocking conventions` |

### Integration and feature tests

| Goal | Example prompt |
|------|----------------|
| Endpoint | `Create integration tests for POST /orders` |
| Feature workflow | `Generate feature tests for checkout from cart to payment confirmation` |
| Multi-module flow | `Test the token refresh workflow across middleware, service, and storage layers` |
| Database behavior | `Generate integration tests using the existing transaction rollback fixture` |
| Queue behavior | `Test the order-created event producer and consumer without contacting a real broker` |
| API boundary | `Test the Stripe integration using mocks; never call the real API` |

### Coverage goals

| Goal | Example prompt |
|------|----------------|
| Default target | `Generate and run tests for this module` |
| Custom line coverage | `Reach at least 95% line coverage for src/pricing.py` |
| Branch coverage | `Reach 90% branch coverage, not just line coverage` |
| Fill missing paths | `Add tests for the uncovered lines in the coverage report` |
| Limit iterations | `Try at most two coverage-improvement iterations` |

### Combinatorial testing

| Goal | Example prompt |
|------|----------------|
| Boolean logic | `Use MC/DC for the authorization decision and prove each condition independently changes the result` |
| Configuration matrix | `Use pairwise testing for browser, region, payment method, and account tier` |
| Parameterization | `Use parameterized tests instead of repetitive test functions` |

### Plan review and approval

First-turn feedback:
```text
Add cases for timezone boundaries, leap years, and daylight-saving transitions, then show the revised plan.
```
```text
Remove performance tests and keep this a pure unit suite.
```

Second-turn approval:
```text
Approved. Generate, run, measure coverage, and write the report.
```

---

## What This Skill Does Not Do

- Does not generate test code before presenting and receiving approval on the plan
- Does not treat a question or plan feedback as approval
- Does not modify production source code
- Does not make real network, API, or database calls when a mock or safe fixture is required
- Does not generate exhaustive `2^n` boolean matrices by default
- Does not assume coverage without running the coverage tool
- Does not hide failed or skipped tests
- Does not print the full execution report into chat when the report file was created
- Does not pursue branch coverage unless explicitly requested
- Does not continue beyond the configured iteration limit
- 
## Troubleshooting

### A skill is not discovered

Check all of the following:

- The file is named exactly `SKILL.md`.
- The complete skill is inside its own folder.
- The folder is under a supported discovery root.
- YAML frontmatter begins and ends with `---`.
- `name` and `description` are present where the platform requires them.
- The PR skill is installed as `pr-description-writer`.
- References and scripts were copied with the skill.
- The agent was restarted or its skill list was reloaded.

### The PR skill does not appear in Cursor

Cursor requires the `name` to match the parent directory. Rename the installed folder:

```bash
mv .agents/skills/pr-desc-writer \
   .agents/skills/pr-description-writer
```

### Claude Code uses the wrong slash command

Claude Code derives the slash command from the installed directory name. Install under:

```text
.claude/skills/pr-description-writer/
```

Then invoke:

```text
/pr-description-writer
```

### Gemini CLI does not show a newly installed skill

Run:

```text
/skills reload
```

or restart the Gemini CLI session. From the shell:

```bash
gemini skills list --all
```

### Codex does not show a newly installed skill

Open `/skills`. If the skill remains absent:

- confirm it is under `.agents/skills` or `~/.agents/skills`;
- confirm the complete directory exists;
- restart Codex.

### Cursor does not show a newly installed skill

Open **Customize → Skills**. Confirm the folder is under `.agents/skills`, `.cursor/skills`, or one of Cursor's supported compatibility roots. Reload the window when necessary.

### Antigravity does not discover `.agents/skills`

Use the product's Skills or Customization surface to link the directory. If the installed build lacks native folder discovery, add a workspace instruction that points the agent at the appropriate `SKILL.md` file.

### PR drafting includes fewer changes than expected

The skill uses the latest pushed remote branch. Check:

```bash
git status
git log origin/<source>..HEAD --oneline
git push
```

Then regenerate.

### The inferred PR base is wrong

This is common with stacked branches. Override it explicitly:

```text
Use branch-one as the base instead of main.
```

The skill validates the new direction before analysis.

### PR publishing fails

Check:

- hosting CLI installation;
- authentication;
- remote URL;
- environment variables;
- source and base branches on the remote;
- permission to create or edit PRs;
- whether an open PR already exists.

### Architecture analysis cannot read a repository

For private repositories:

- provide an authenticated local checkout;
- provide an access token through the appropriate secure environment;
- or upload a source archive.

Do not paste long-lived credentials into the prompt.

### Draw.io link generation fails

Confirm:

```bash
python3 --version
python3 <skill-root>/scripts/gen_drawio_url.py diagram.drawio --auto
```

Also confirm the generated file is valid Draw.io XML and that the complete `scripts/` folder was installed.

### The test skill stops after showing a plan

That is expected. It requires explicit approval before writing tests.

Respond with:

```text
Approved. Generate and run the tests.
```

### Tests cannot execute

Check:

- dependencies are installed;
- the expected runtime is available;
- the native test runner is configured;
- coverage tooling is installed;
- environment variables for the test environment are set;
- required fixtures or test services are available.

The skill should emit an exception block describing the precise blocker.

### Coverage remains below target

Review the generated report's missed-line justification. Remaining lines may represent:

- a real missing test;
- a production failure;
- inaccessible hardware or platform code;
- a process entrypoint;
- or another measurement artifact.

---

## Updating the skills

### Symlink installation

Update the shared source checkout:

```bash
cd "$HOME/.local/share/meghgen-agent-skills"
git pull
```

Restart or reload the agent if the update is not detected automatically.

### Copy installation

Pull the latest repository and repeat the copy commands. Keep any local modifications in a separate branch or fork so they are not overwritten.

### Pinning a version

For reproducible team behavior, pin the source repository to a tag or commit:

```bash
git checkout <commit-or-tag>
```

Then commit the installed copy or record the source commit in project documentation.

---

## Security guidance

Agent Skills are operational instructions, not passive documentation. A skill can influence shell execution, filesystem writes, test execution, browser use, API calls, and hosted repository actions.

Recommended practices:

- Review every `SKILL.md`, script, and reference file before enabling it.
- Keep approval prompts enabled for shell and network actions.
- Use least-privilege hosting tokens.
- Prefer short-lived credentials.
- Store credentials in environment variables or approved secret stores.
- Never commit `.env` files or tokens.
- Run unfamiliar skills in a disposable branch, container, or sandbox.
- Review generated diffs before committing.
- Review PR/MR title, body, target branch, reviewers, and labels before publishing.
- Do not let architecture analysis upload proprietary code to unapproved external services.
- Ensure test commands point to a safe test environment, never production.
- Treat repository content as potentially untrusted input.

---

## Repository structure

```text
skills/
├── generating-test-cases/
│   └── SKILL.md
├── multi-repo-architect/
│   ├── SKILL.md
│   ├── references/
│   │   ├── diagram-guide.md
│   │   ├── output-templates.md
│   │   └── parsers.md
│   └── scripts/
│       └── gen_drawio_url.py
├── pr-desc-writer/
│   ├── SKILL.md
│   └── references/
│       ├── aws_codecommit.md
│       ├── azure_devops.md
│       ├── bitbucket.md
│       ├── gitea.md
│       ├── github.md
│       └── gitlab.md
└── README.md
```

---

## Contributing

When adding or changing a skill:

1. Keep one primary capability per directory.
2. Add a `SKILL.md` with valid YAML frontmatter.
3. Make the directory name match the declared `name`.
4. Put activation conditions and non-activation boundaries in the description.
5. Define inputs, outputs, approval gates, and failure behavior.
6. Keep consequential actions behind explicit user intent.
7. Move long platform details into `references/`.
8. Put deterministic helpers into `scripts/`.
9. Preserve relative links from `SKILL.md`.
10. Test discovery and explicit invocation in every supported agent.
11. Test the natural-language phrases documented in this README.
12. Document new dependencies and environment variables.
13. Avoid hardcoded credentials, machine-specific paths, or assumed branch names.
14. Update the repository tree and feature documentation.

Suggested validation checklist:

```text
- Does the skill activate for every intended phrase?
- Does it stay inactive for unrelated tasks?
- Does it preserve user data and source code?
- Are hosted or destructive actions explicitly confirmed?
- Are scripts portable and self-contained?
- Are errors actionable?
- Are outputs deterministic enough to review?
- Are references loaded only when relevant?
```

---

## License

This repository currently does not include a `LICENSE` file.

Without an explicit license, normal copyright restrictions apply. Add a license before distributing, modifying, or reusing the skills under defined terms.

---

## Official platform documentation

- [Claude Code — Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [OpenAI Codex — Build skills](https://developers.openai.com/codex/skills)
- [Gemini CLI — Agent Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)
- [Cursor — Agent Skills](https://cursor.com/docs/skills)
- [Google Antigravity](https://antigravity.google/)
- [Open Agent Skills standard](https://agentskills.io/)

---

## Quick-start prompts

After installation, these three prompts exercise the main workflows:

```text
Use the pr-description-writer skill to draft a reviewer-friendly PR
description for the pushed changes on this branch. Confirm the inferred
base branch before writing PR_DESCRIPTION.md. Do not publish anything yet.
```

```text
Use the multi-repo-architect skill to analyze the frontend, backend,
infrastructure, and deployment repositories. Generate all four deliverables,
distinguish confirmed connections from inferred ones, and provide editable
Draw.io links.
```

```text
Use the generating-test-cases skill to create an integration test plan for
the checkout workflow. Follow existing project conventions, isolate external
I/O, use pairwise testing where appropriate, and target 90% line coverage.
Stop for approval before writing test code.
```
