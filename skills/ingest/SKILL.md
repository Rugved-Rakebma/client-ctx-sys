---
name: ingest
description: Process a Fireflies meeting into the knowledge base
allowed-tools: Bash, Read, Write
user-invocable: true
disable-model-invocation: true
argument-hint: "<fireflies-url> or --latest"
---

# KB Ingest

Ingest a Fireflies meeting transcript into the knowledge base.

## HARD RULES

1. **NEVER write entity files.** All entities go into the DB via `just kb-add`.
2. **NEVER use the Read tool on raw Fireflies JSON files.** Use CLI output only.
3. **ALWAYS file the meeting doc** in `.knowledge-base/docs/meetings/`.
4. **ALWAYS run `just kb-status`** after adding entities.
5. **People: only track meeting participants**, not everyone mentioned. Someone discussed is not a person to track.
6. **NEVER spawn subagents.** Do all work in this context.

## Reference

See `references/entity-extraction.md` for entity extraction guidelines.

## Pre-injection

- Run `just kb-status 2>/dev/null`

## Ingest Paths

### Fireflies URL

If the argument contains `app.fireflies.ai`:

1. Run `just kb-pull-fireflies --url "<url>"`
2. Use the CLI output directly — it contains the structured summary
3. **Do NOT read the raw JSON file.**

### Latest from Fireflies

If the argument is `--latest` or `--from-fireflies --latest`:

1. Run `just kb-pull-fireflies --latest`
2. Same as URL path — use CLI output directly

## Flow

### Step 1: Extract entities

From the meeting content, extract entities following the guidelines in `references/entity-extraction.md`. For each entity, check if it already exists via `just kb-list --type <type>`.

Entity types emerge from content. Common types: `decisions`, `action-items`, `requirements`, `strategies`. Use what fits.

**Action item status:** New action items always get `"status": "open"`. When cross-referencing reveals an existing action item that the meeting resolves or completes, include it in the same staging batch with `"status": "completed"` and updated content reflecting how it was resolved.

### Step 2: Propose meeting doc

Propose filing a clean meeting summary at:
`.knowledge-base/docs/meetings/YYYY-MM-DD-<slug>.md`

The doc should have frontmatter:
```yaml
---
title: "Meeting Title"
date: YYYY-MM-DD
source: "Fireflies URL or transcript ID"
participants:
  - Name One
  - Name Two
---
```

Followed by a clean summary (not raw transcript).

### Step 3: Present proposals

Present everything for approval in ONE list:
- Entities to create/update (with type, slug, title, content preview)
- People to create/update (participants only — Hard Rule #5)
- Meeting doc location and content summary

**Wait for explicit user approval before writing anything.**

### Step 4: Store (on approval)

**4a. Entities and people** — Build JSON and run `just kb-add '<json>'`:
```json
{
  "source": {
    "type": "meeting",
    "title": "Meeting Title",
    "path": "docs/meetings/YYYY-MM-DD-slug.md",
    "original_source": "fireflies-url"
  },
  "entities": [
    { "type": "decisions", "slug": "my-slug", "title": "Title", "content": "Full content..." },
    { "type": "action-items", "slug": "new-task", "title": "New Task", "content": "Details...", "status": "open" },
    { "type": "action-items", "slug": "old-task", "title": "Old Task — Completed", "content": "Resolved in this meeting because...", "status": "completed" }
  ],
  "people": [
    { "name": "Jane Doe", "slug": "jane-doe", "role": "Engineer", "org": "Acme" }
  ]
}
```

**Always** write the JSON to `.knowledge-base/.staging.json` and run `just kb-add .knowledge-base/.staging.json`. Never pass JSON inline on the command line. The CLI clears the staging file automatically after a successful write.

**4b. Meeting doc** — Write the meeting summary to `.knowledge-base/docs/meetings/YYYY-MM-DD-slug.md`.

### Step 5: Confirm

- Run `just kb-status` and report what was added.

## Key Behaviors

- Capture **WHY** not just WHAT — rationale, context, and reasoning matter.
- **Propose, never auto-apply.** All writes require user approval.
- Cross-reference new entities against existing ones to detect updates and contradictions.
