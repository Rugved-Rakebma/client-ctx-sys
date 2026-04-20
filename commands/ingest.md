---
description: Process a Fireflies meeting into the context vault
disable-model-invocation: true
argument-hint: "<fireflies-url> or --latest [--full]"
---

# Context Ingest

Ingest a Fireflies meeting transcript into the context vault. Extracts entities, updates project overviews, enriches people pages, maintains wikilinks.

## Hard Rules

1. **Wait for explicit approval** before writing any files
2. **Always use Obsidian wikilinks** — `[[type/slug|Display Text]]`
3. **People: only track meeting participants**, not everyone mentioned
4. **Update project overviews** — every new entity must be linked from its project overview
5. **Only spawn a subagent for `--full` transcript filing**

## Ingest Paths

### From Fireflies URL

If the argument contains `app.fireflies.ai`:

1. Run `python3 ~/Code/client-ctx-sys/scripts/pull-fireflies.py --url "<url>"`
2. Use the CLI output — it contains the structured summary
3. Do NOT read the raw JSON file. Entity extraction uses the summary only.

### Latest from Fireflies

If the argument is `--latest`:

1. Run `python3 ~/Code/client-ctx-sys/scripts/pull-fireflies.py --latest`
2. Same as URL path.

## Workflow

### Step 1: Extract entities from meeting content

Read the CLI output (summary, action items, outline, keywords).

Identify:
- **Decisions** — explicit choices with rationale
- **Action items** — assigned to someone with a deliverable (new → `status: "open"`, resolved → `status: "completed"`)
- **Strategies** — high-level approach frameworks (rare)
- **Requirements** — hard constraints (rare)
- **People** — meeting participants only

Check existing entities: grep the vault for potential duplicates before proposing new ones.

### Step 2: Determine project mapping

For each entity, determine which project(s) it belongs to. Read `context-vault/projects/` overviews to match.

### Step 3: Propose meeting doc

Propose filing at: `context-vault/docs/meetings/YYYY-MM-DD-{slug}.md`

Frontmatter:
```yaml
---
title: "Meeting Title"
date: YYYY-MM-DD
source: "Fireflies URL"
participants:
  - Name One
  - Name Two
---
```

- **Without `--full`:** Clean summary with key topics, decisions, and action items.
- **With `--full`:** Full speaker-attributed transcript filed by a subagent using `format-transcript` CLI command.

### Step 4: Present proposals

Present everything for approval in ONE list:
- Entities to create/update (type, slug, title, content preview, project assignment)
- People to create/update (participants only)
- Meeting doc location and content approach
- Project overviews that will be updated

**Wait for explicit user approval.**

### Step 5: Write (on approval)

1. **Entity pages** — Write to `context-vault/{type}/{slug}.md` with frontmatter, content, and Links section (source, assignees, related entities from same meeting). Use Obsidian-flavored markdown conventions (`obsidian:obsidian-markdown` skill) if available; standard markdown with `[[wikilink]]` syntax otherwise.

2. **Meeting doc** — Write with content + Knowledge Graph section (wikilinks to all entities + participant links)

3. **People pages** — Create or update: add new action items, meetings attended, decisions

4. **Project overviews** — Add new entities as wikilinks in correct sections

5. **Index and log** — Update `context-vault/index.md` tables. Append to `context-vault/log.md`.

### Step 6: Confirm

Report what was written: entities created/updated, meeting doc path, overviews updated, people updated.
