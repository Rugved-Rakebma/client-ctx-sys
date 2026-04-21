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
skills/             # ctx-init (user-invocable), context-prime, context-status, context-update (model-invocable)
  init/             # /ctx:init — scaffolds context vault, includes templates/
  context-prime/    # Auto-prime project context at session start
  context-status/   # Generate session briefing from vault data
  context-update/   # Update vault pages after session changes
scripts/            # pull-fireflies.py, format-transcript.py, statusline.py
settings.json       # StatusLine config
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/pull-fireflies.py` | Fetch transcript from Fireflies API (stdlib only) |
| `scripts/format-transcript.py` | Format raw JSON into speaker-attributed markdown |
| `scripts/statusline.py` | Status bar — reads context-vault, outputs one-liner |

All scripts use Python 3.9.6 stdlib only (no pip dependencies).

## Testing

```
claude --plugin-dir /path/to/client-mgt-market
```
