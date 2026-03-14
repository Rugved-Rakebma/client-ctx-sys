# Knowledge Base — Architecture

## What This Is

A per-project knowledge base for client engagements. Captures meetings, documents, decisions, and requirements. Makes them searchable and queryable via Claude Code skills.

Not a project driver — a filing cabinet. The database is the store. Filed documents live alongside it.

## Project Structure

```
~/Code/knowledge-base/           # Plugin source
├── cli/                         # Python CLI (Click)
│   ├── kb.py                    # Entry point
│   ├── commands/
│   │   ├── init.py              # Scaffold .knowledge-base/
│   │   ├── status.py            # DB stats
│   │   ├── list_cmd.py          # List entities
│   │   ├── get.py               # Read one entity
│   │   ├── add.py               # Insert/update entities, people, relations
│   │   ├── search.py            # FTS5 search with BM25
│   │   └── pull_fireflies.py    # Fetch from Fireflies API
│   └── db/
│       └── schema.py            # SQLite schema, FTS triggers, migrations
├── skills/
│   ├── init/SKILL.md            # Initialize KB in a project
│   ├── ingest/SKILL.md          # Ingest Fireflies meetings
│   ├── ingest/references/       # Entity extraction guidelines
│   ├── search/SKILL.md          # Search and synthesize answers
│   ├── status/SKILL.md          # Show KB stats
│   ├── maintain/SKILL.md        # Clean up duplicates/contradictions
│   └── catalog/SKILL.md         # File documents with frontmatter
├── templates/
│   ├── config.yaml              # Default project config
│   ├── justfile.snippet         # Just recipes injected into projects
│   └── claude-kb-section.md     # CLAUDE.md section injected into projects
└── hooks/
    └── hooks.json               # Empty (no hooks)
```

## Target Project Structure

When KB is initialized in a project:

```
~/Project/
├── .env                         # FIREFLIES_API_KEY lives here
├── justfile                     # Has kb-* recipes (from justfile.snippet)
├── CLAUDE.md                    # Has KB section (from claude-kb-section.md)
├── .knowledge-base/
│   ├── config.yaml              # Project name, Fireflies config
│   ├── .gitignore               # Excludes DB, staging, raw/
│   ├── knowledge-base.db        # SQLite: entities, people, relations, FTS
│   ├── file-manifest.yaml       # Catalog of filed documents
│   └── docs/                    # Filed source documents
│       └── meetings/            # Meeting summaries
```

## Two Layers

1. **Skills** — Workflow orchestration. Define what happens when user runs `/kb:ingest`, `/kb:search`, etc. Claude follows the skill instructions.
2. **CLI** — Deterministic work. All output is JSON. Called via `just kb-*` recipes.

Claude does semantic work (extraction, synthesis). CLI does mechanical work (DB operations, API calls, search).

## Storage Model

- **Database is the store.** `knowledge-base.db` holds entities, people, relations, sources, and FTS index. All via `kb add`.
- **Docs are filed documents.** Meeting summaries, client docs — stored as markdown in `.knowledge-base/docs/` with frontmatter.
- **`file-manifest.yaml`** — catalog of all filed documents. Updated by the catalog skill.
- **Entity types are dynamic.** They emerge from content during ingest, not predefined.
- **No markdown entity files.** The old `entities/<type>/<slug>.md` pattern is gone. Everything is in the DB.

## Search

SQLite FTS5 with BM25 ranking. Built into macOS system SQLite — zero extensions, zero external APIs.

- `kb add` automatically updates the FTS index via triggers (no separate index command)
- `kb search` does prefix wildcard matching + LIKE fallback

## Dependencies

3 Python packages (Python 3.9.6 compatible):
- click (CLI framework)
- httpx (Fireflies API)
- pyyaml (config files)

## Design Decisions

### DB-first, not markdown-first
Entities live in SQLite, not as individual markdown files. This gives us FTS for free via triggers, relational links between entities, and atomic batch operations. No separate index/rebuild step.

### No agents
The kb-manager agent was never invoked by Claude Code. Skills are the execution unit — Claude reads the SKILL.md and follows it directly in the conversation context.

### No `context: fork`
Fork context was an unverified assumption about Claude Code's execution model. All skills run in the main conversation context.

### Only `search` is model-invocable
Search is the only skill that Claude can invoke proactively (without the user typing `/kb:search`). All other skills are user-initiated only.
