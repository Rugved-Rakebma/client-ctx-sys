# Knowledge Base Plugin — Development Guide

## Architecture

Two layers, strict separation of concerns:

1. **Skills** — Orchestration layer. Claude reads files, proposes changes, asks for approval. Skills define the workflow.
2. **CLI** (`cli/kb.py`) — Deterministic work. Storage, search, Fireflies API. All output is JSON.

Skills orchestrate. CLI does deterministic work. Claude does semantic work (extraction, synthesis, summarization).

**Database is the store.** All entities, people, relations, and FTS index live in `knowledge-base.db`. No markdown entity files. Docs (meetings, client docs) are filed in `.knowledge-base/docs/` and cataloged in `file-manifest.yaml`.

## Python Compatibility

Target: Python 3.9.6 (macOS system Python).

- No `match` statements (3.10+)
- No `X | Y` union types (3.10+)
- Use `from __future__ import annotations` in every module
- Use `typing.Optional`, `typing.Union`, `typing.List`, `typing.Dict` for type hints

## CLI Output

All CLI commands emit JSON to stdout. Human-readable output goes to stderr. This lets skills parse output reliably.

## CLI Commands

| Command | Purpose |
|---------|---------|
| `kb init` | Scaffold `.knowledge-base/` with DB |
| `kb status` | Entity counts, people, sources, DB size, open action items |
| `kb list [--type TYPE] [--status STATUS]` | List entities with optional type/status filter |
| `kb get <type/slug>` | Read one entity |
| `kb add <json>` | Insert/update entities, people, relations |
| `kb search "<query>"` | Full-text search with BM25 ranking |
| `kb pull-fireflies` | Fetch transcript from Fireflies API |

## Just Recipes

All project-side commands use `just` recipes. Never run raw `python3` commands in skills (except `/kb:init` which bootstraps the recipes).

## Dev Commands

```
just kb --help       # CLI help
just install-deps    # Install Python dependencies
just test            # Run tests
```

## Testing the Plugin

```
claude --plugin-dir ~/Code/knowledge-base
```

This loads the plugin with all skills.

## Skills

| Skill | Purpose | Model-invocable? |
|-------|---------|-----------------|
| `/kb:init` | Scaffold KB, inject CLAUDE.md section + justfile recipes | No |
| `/kb:ingest` | Fireflies meetings → extract → propose → approve → store | No |
| `/kb:search` | Search DB, read results, synthesize answer | **Yes** |
| `/kb:status` | Run kb-status, present facts | No |
| `/kb:maintain` | Find duplicates/contradictions, propose cleanup | No |
| `/kb:catalog` | File a document into docs/ with frontmatter | No |
