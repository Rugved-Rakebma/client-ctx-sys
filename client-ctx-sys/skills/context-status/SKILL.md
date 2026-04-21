---
name: context-status
description: Generate a session briefing from context vault data
allowed-tools: Bash, Read, Glob, Grep
user-invocable: false
---

# Context Status

Generate a session briefing by reading context vault files directly. Called proactively when Claude needs to understand current state.

## Workflow

1. Find the context vault — look for `context-vault/` in the current directory or parent directories.

2. Read `context-vault/index.md` for the project inventory.

3. Scan `context-vault/action-items/` for open items:
   - Read frontmatter of each file
   - Collect items where `status: "open"` or `status: open`
   - Note owner (from slug prefix or content) and created date

4. Read `context-vault/log.md` for the most recent source/meeting.

5. Return structured data:
   - Open action items with owners, grouped by project if possible
   - Number of entities by type
   - Last meeting date and title
   - Project inventory with statuses

## Output

Return the briefing data to the calling context. Format as a clean summary — not raw file contents.
