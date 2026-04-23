# Client Context System — Development Guide

## Architecture

File-first wiki system for client project context management. No database. Claude reads and writes markdown files directly.

Two layers:

1. **Commands** (`/ctx:*`) — User-invocable workflows in `commands/`. Flat `.md` files. The plugin name `"ctx"` creates the `/ctx:` prefix.
2. **Skills** — In `skills/`. Each skill is a directory with `SKILL.md`. Can be user-invocable (`user-invocable: true`) or model-invocable only (`user-invocable: false`).

**Context vault is the store.** All entities live as markdown files in `context-vault/` in the target project. Obsidian-compatible wikilinks connect everything.

## Plugin Structure

```
commands/           # /ctx:prime, /ctx:project, /ctx:ingest, /ctx:status, /ctx:maintain, /ctx:catalog
skills/
  init/             # /ctx:init — scaffolds context vault, includes templates/
  ctx-prime/        # Auto-prime project context at session start (model-invocable)
  ctx-status/       # Generate session briefing from vault data (model-invocable)
  ctx-update/       # Update vault pages after session changes (model-invocable)
scripts/            # pull-fireflies.py, format-transcript.py, statusline.py
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/pull-fireflies.py` | Fetch transcript from Fireflies API (stdlib only) |
| `scripts/format-transcript.py` | Format raw JSON into speaker-attributed markdown |
| `scripts/statusline.py` | Two-line status bar — session info from stdin JSON + vault state from filesystem |

All scripts use Python 3.9.6 stdlib only (no pip dependencies).

## Testing

```
claude --plugin-dir /path/to/client-mgt-market
```
