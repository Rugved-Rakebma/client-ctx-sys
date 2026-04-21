---
description: Session briefing from context vault
disable-model-invocation: true
---

# Context Status

Present a session briefing by reading the context vault directly.

## Workflow

### 1. Find the context vault

Look for `context-vault/` in the current directory or parent directories.

### 2. Gather data

- **Open action items**: Scan `context-vault/action-items/*.md` frontmatter for `status: "open"`. Extract title, slug, created date. Determine owner from slug prefix.
- **Project inventory**: Read `context-vault/index.md` Projects table — list each project with its status.
- **Recent activity**: Read `context-vault/log.md` — last 3 entries.
- **Entity counts**: Count files in each entity directory.

### 3. Present briefing

**Needs Attention**
- Open action items grouped by owner, sorted by age (oldest first)
- Flag any items older than 14 days as stale

**Projects**
- Each project with current status (from overview frontmatter)

**Recent Activity**
- Last 3 sources from log.md with dates

**Inventory**
- Entity counts by type (compact, one line)

### Tone

Briefing style. Facts only. No suggestions, no apologies, no filler.
