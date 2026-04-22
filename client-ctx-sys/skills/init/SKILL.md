---
name: init
description: Initialize the context system in a client project
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Context Init

Set up the client context system in the current project. Idempotent — safe to run on both fresh projects and projects with existing context vaults.

Templates for scaffolding live alongside this skill in `templates/`.

## Workflow

### 1. Detect existing state

Check what already exists:
- Does `context-vault/` exist?
- Does `.claude/rules/context-vault.md` exist?
- Does `CLAUDE.md` contain a "## Context Vault" section?
- What projects exist in `context-vault/projects/`?
- Which projects already have `.claude/rules/project-{slug}.md`?

Report what was found.

### 2. Scaffold context vault (if missing)

If `context-vault/` does not exist, create:

```
context-vault/
├── index.md              # Master index with header and empty section tables
├── log.md                # Log with header
├── projects/
├── decisions/
├── action-items/
├── strategies/
├── requirements/
├── people/
├── docs/
│   ├── meetings/
│   ├── client-docs/
│   └── deliverables/
├── config.yaml           # From templates/config.yaml, with project name filled in
├── dashboard.base        # Obsidian Bases dashboard
└── .gitignore            # From templates/gitignore
```

**index.md and log.md:** Use Obsidian-flavored markdown conventions (`obsidian:obsidian-markdown` skill) if available — properties frontmatter, callouts for navigation hints, wikilinks for section anchors. Otherwise write plain markdown with standard YAML frontmatter and `[[wikilink]]` syntax.

**dashboard.base:** Use the `obsidian:obsidian-bases` skill if available to generate the dashboard with views tailored to the projects found during detection (Step 1). If the skill is not available, copy from `templates/dashboard.base` as a static fallback.

If `context-vault/` already exists but `dashboard.base` is missing, generate or copy it using the same logic above.

If `context-vault/` already exists and `dashboard.base` exists, skip.

### 3. Filesystem audit

Before creating any rules, cross-reference the vault against the filesystem:

- List physical project directories: `ls projects/`
- List vault project entries: `ls context-vault/projects/`
- Cross-reference and flag:
  - **Phantom vault projects** — vault entry exists but no physical dir under `projects/`. Warn and do NOT create rules for these.
  - **Untracked physical projects** — physical dir exists but no vault entry. Report and suggest `/ctx:project`.
  - **Naming mismatches** — vault slug differs from physical dir name. Report.

For each **valid** project (both vault entry AND physical dir exist):
- Detect the actual context page filename in the vault project dir (could be `ctx-{slug}.md`, `overview.md`, or something else)
- Use the detected filename when creating the rule — do not assume the template default

Report the audit results before proceeding.

### 4. Install the always-loaded rule

If `.claude/rules/context-vault.md` does not exist, copy from `templates/context-vault-rule.md`. This rule has empty frontmatter (no `paths:`) so it loads every session.

If it already exists, skip.

### 5. Install project-level rules

For each valid project from the audit (both vault + physical dir):

If `.claude/rules/project-{slug}.md` does not already exist:
- Read the project context page to get the title
- Write `.claude/rules/project-{slug}.md` using `templates/project-prime-rule.md` as the base, with `paths:` scoped to `projects/{slug}/**/*`
- Reference the actual detected filename in the rule body

Report how many project rules were created.

### 6. Update CLAUDE.md

If `CLAUDE.md` does not exist, create it with the Context Vault section from `templates/claude-ctx-section.md`.

If `CLAUDE.md` exists but does not contain a "## Context Vault" section, append the section from `templates/claude-ctx-section.md`.

If it already contains the section, replace ONLY that section (from `## Context Vault` to the next `## ` heading or end of file) with the latest template. This ensures the section stays current without touching other content.

### 7. Configure statusline

Read `.claude/settings.json` (or `.claude/settings.local.json`). If no `statusLine` config exists, add:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.py context-vault/"
  }
}
```

`${CLAUDE_PLUGIN_ROOT}` resolves to this plugin's installed path. The model sees the concrete path and writes it into settings.json.

If the file already has other settings, merge the `statusLine` key without overwriting existing config. If a `statusLine` config already exists, skip.

### 8. Stale footprint cleanup (migrated projects)

Check for remnants of the old KB CLI system. Only relevant for projects migrating from the previous `k-base` plugin:

- Justfile with `kb-*` or `kb_cli` recipes → report
- `.claude/settings.local.json` or `.claude/settings.json` with `kb-*` or `k-base:*` permissions → report
- `config.yaml` with `fireflies:` section from old system → report
- CLAUDE.md with `## Knowledge Base` section (old, not `## Context Vault`) → report
- Obsidian workspace files (`.obsidian/workspace.json`) with `.knowledge-base/` or `knowledge-base/` paths → report
- `people/` alias stubs with `alias_of` frontmatter → report (should be deleted if canonical page exists)
- `<!-- kb-enriched:v1 -->` HTML comments in entity pages → note (cosmetic, low priority)

Present all findings. Propose cleanup actions. **Wait for approval** before making any changes.

### 9. Report

Summary of what was done:
- Vault: created / already existed
- Filesystem audit: N valid projects, N phantoms, N untracked
- Rules: N created, N already existed, N skipped (phantom)
- CLAUDE.md: created / updated / already current
- Statusline: configured / already existed
- Stale cleanup: N items found / cleaned / skipped
- Remind user to run `/ctx:project <name>` to add new projects
