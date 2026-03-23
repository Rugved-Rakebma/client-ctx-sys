# Knowledge Base — Architecture

## What This Is

A Claude Code plugin that gives Claude persistent, per-project memory for client engagements. Captures meetings (via Fireflies), documents, decisions, action items, requirements — makes them searchable and queryable across sessions.

Not a project driver — a filing cabinet. The database is the store. Filed documents live alongside it.

## Why This Exists

Client work generates a constant stream of decisions, action items, and context spread across meetings and documents. Without this, every Claude session starts from zero — no memory of what was decided, what's outstanding, or who's involved. This plugin gives Claude the ability to accumulate and recall project knowledge across conversations.

## The Rebuild — What We Learned

The v1 architecture was built on unverified assumptions about how Claude Code executes plugins:

- **`kb-manager` agent** was never invoked by any session. Claude Code doesn't dispatch to named agents the way we assumed.
- **`context: fork`** was fictional. No such execution model exists.
- **`allowed-tools`** isn't enforced by Claude Code. It's advisory at best.
- **Subagents** spawned without skill context and improvised multi-step procedures, failing every time.

The CLI and storage layer were solid. The entire orchestration layer needed a top-down rethink based on what Claude Code *actually* provides — a prompt discovery mechanism, not a framework.

### The Core Insight

Claude is excellent at understanding, extracting, cross-referencing, and proposing. Claude is unreliable at executing multi-step deterministic procedures. Every ingest failed at the mechanical storage phase because Claude would improvise steps, skip steps, or hallucinate tool behavior.

This insight drives the entire architecture: **Claude does semantic work, CLI does mechanical work.** The boundary is approval — Claude proposes, user approves, then one CLI command handles the rest. Minimize tool calls post-approval.

## Two Layers

1. **Skills** — Prompt documents that define workflows. Claude reads the SKILL.md and follows it directly in conversation context. They are not execution environments — they're instructions.
2. **CLI** (`cli/kb.py`) — Deterministic work. Storage, search, Fireflies API. All output is JSON. Called via `just kb-*` recipes from target projects.

| Responsibility | Owner |
|---|---|
| Entity extraction, synthesis, summarization | Claude (semantic) |
| Cross-referencing, duplicate detection | Claude (semantic) |
| Proposing changes, presenting for approval | Claude (semantic) |
| DB reads/writes, FTS search, API calls | CLI (deterministic) |
| Schema migrations, index maintenance | CLI (deterministic) |

## Project Structure

```
~/Code/knowledge-base/           # Plugin source
├── cli/                         # Python CLI (Click)
│   ├── kb.py                    # Entry point
│   ├── commands/
│   │   ├── init.py              # Scaffold .knowledge-base/
│   │   ├── status.py            # DB stats + open action items
│   │   ├── list_cmd.py          # List entities (filterable by type, status)
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
│   ├── status/SKILL.md          # Show KB stats + open items
│   ├── maintain/SKILL.md        # Status triage + cleanup
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

## Storage Model

- **Database is the store.** `knowledge-base.db` holds entities, people, relations, sources, and FTS index. All writes go through `kb add`.
- **Docs are filed documents.** Meeting summaries, client docs — stored as markdown in `.knowledge-base/docs/` with frontmatter. These are source material, not the knowledge itself.
- **`file-manifest.yaml`** — catalog of all filed documents. Updated by the catalog skill.
- **Entity types are dynamic.** They emerge from content during ingest (`decisions`, `action-items`, `requirements`, `strategies`, etc.), not predefined.
- **Entity lifecycle.** Entities have an optional `status` field. Action items use `open` → `completed`. Status is set during ingest (new items are `open`), updated when meetings resolve them, and triaged by the maintain skill. NULL for entity types that don't need lifecycle tracking. This was added after 2 ingests + 1 catalog on Recirq showed action items piling up with no way to close them — the second ingest correctly identified items to close but had no mechanism to do so.
- **No markdown entity files.** The old `entities/<type>/<slug>.md` pattern is gone. Everything is in the DB.

## Search

SQLite FTS5 with BM25 ranking. Built into macOS system SQLite — zero extensions, zero external APIs.

- `kb add` automatically updates the FTS index via triggers (no separate index command)
- `kb search` does prefix wildcard matching + LIKE fallback
- Status-aware queries: for "what's open/pending" questions, the search skill uses `kb list --status open` instead of FTS

## Dependencies

3 Python packages (Python 3.9.6 compatible — macOS system Python):
- click (CLI framework)
- httpx (Fireflies API)
- pyyaml (config files)

## Design Decisions

### DB-first, not markdown-first
Entities live in SQLite, not as individual markdown files. This gives us FTS for free via triggers, relational links between entities, and atomic batch operations. No separate index/rebuild step.

### Skills are prompts, not execution environments
Skills are SKILL.md files that Claude reads and follows. They define workflows ("extract entities, propose, wait for approval, run kb-add") but don't enforce anything programmatically. This matches what Claude Code actually provides — prompt discovery, not a plugin framework.

### No agents
The kb-manager agent was never invoked by Claude Code. Agents were an abstraction that didn't map to reality. Skills are the execution unit — Claude reads the SKILL.md and follows it directly in the conversation context.

### No `context: fork`
Fork context was an unverified assumption about Claude Code's execution model. All skills run in the main conversation context.

### Only `search` is model-invocable
Search is the only skill Claude can invoke proactively (without the user typing `/kb:search`). This is intentional — Claude should reach into the KB when conversation touches decisions, requirements, or history. All other skills are user-initiated because they involve writes that need approval.

### Minimize post-approval tool calls
The biggest lesson from v1: Claude fails at multi-step mechanical procedures after approval. The fix is architectural — push all mechanical work into single CLI commands. `kb add` takes a full JSON batch (entities, people, relations, source) and handles everything atomically. Claude's job ends at building the JSON and getting approval.

### Schema migrations run on every connection
`get_db()` runs migrations, not just `init_db()`. This means any command (`kb list`, `kb add`, etc.) will transparently migrate an older database. No manual migration step, no version mismatch errors.
