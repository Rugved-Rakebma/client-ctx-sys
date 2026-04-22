---
description: Complete system guide — commands, lifecycle, entity model, conventions
disable-model-invocation: true
---

# Client Context System — Guide

A file-first context management system for client projects. Maintains a persistent, compounding knowledge graph as markdown files with Obsidian-compatible wikilinks. No database — Claude reads and writes files directly.

## Why This Exists

The core problem is **context assembly**. When you start a session, Claude needs to be fully primed with the right context — and when the session ends, nothing important should be lost. The context vault is the persistent memory layer that makes this work.

## The Context Vault

Lives at `context-vault/` in the client project root. Contains:

```
context-vault/
├── index.md                          # Master navigation
├── log.md                            # Chronological ingest history
├── projects/
│   └── {slug}/ctx-{slug}.md          # Project context pages (prime pages)
├── decisions/{slug}.md               # Architectural and strategic choices
├── action-items/{slug}.md            # Tracked tasks with owner + status
├── strategies/{slug}.md              # Approach frameworks
├── requirements/{slug}.md            # Hard constraints
├── people/{slug}.md                  # Participants with linked entities
├── docs/
│   ├── meetings/{date-slug}.md       # Meeting records with backlinks
│   ├── client-docs/                  # Documents from the client
│   ├── deliverables/                 # Documents produced for the client
│   └── research/                     # Protocol refs, tech evaluations, general research
└── archive/                          # Completed/superseded items (created by maintain)
```

## Commands

### Lifecycle

```
SETUP           INPUT            ACCESS           OUTPUT          HEALTH
/ctx:init       /ctx:ingest      /ctx:prime       /ctx:convo      /ctx:maintain
/ctx:project    /ctx:catalog     /ctx:status
```

### Setup Commands

**`/ctx:init`** — Initialize the context system in a client project. One-time setup: scaffolds the vault, installs rules, configures CLAUDE.md and statusline. Audits filesystem for mismatches. Cleans stale references from old systems. Safe to re-run.

**`/ctx:project <name>`** — Scaffold a new project. Creates the vault context page and a path-scoped auto-prime rule. A project should exist when it has a distinct deliverable, spans multiple sessions, and typically has its own codebase.

### Input Commands

**`/ctx:ingest <url|--latest>`** — Process a Fireflies meeting transcript. Extracts decisions, action items, people. Updates project context pages, people pages, index, and log. All changes proposed and approved before writing.

**`/ctx:catalog <path>`** — File a document into the vault. Adds frontmatter, categorizes (client-docs, deliverables, research), and links from relevant project context pages.

### Access Commands

**`/ctx:prime <anything>`** — Deep context assembly. Takes a project, person, topic, or meeting. Reads vault context + actual project files + current state. Synthesizes a complete briefing. This is the "dive into X" command.

**`/ctx:status`** — Quick vault health snapshot. Open action items by owner, project inventory, recent activity. Vault-only, broad and shallow. This is the "what needs attention?" command.

**Prime vs Status:**
- Status = broad, shallow, vault-only → "What's the state across all projects?"
- Prime = narrow, deep, multi-source → "Tell me everything about THIS thing."

### Output Commands

**`/ctx:convo`** — End-of-session context capture. Reviews what happened during the session. Identifies decisions, action items, status changes, and new information that should be filed in the vault. Run before closing a session to ensure nothing important is lost.

### Health Commands

**`/ctx:maintain`** — Comprehensive vault maintenance. 5 interactive phases: structural audit, entity health, relationship integrity, archive/cleanup, and report. Run periodically to keep the vault clean.

**`/ctx:help`** — This guide.

## Entity Model

| Entity | Directory | Frontmatter | Notes |
|--------|-----------|-------------|-------|
| Project | `projects/{slug}/` | title, status, priority | Context page links to all project entities |
| Decision | `decisions/{slug}.md` | title, type, slug, status, source, created, updated | Capture rationale, not just the choice |
| Action Item | `action-items/{slug}.md` | title, type, slug, status, source, created, updated | Slug convention: `owner-verb-noun`. Status: open/completed |
| Strategy | `strategies/{slug}.md` | title, type, slug, status, source, created, updated | High-level approach frameworks |
| Requirement | `requirements/{slug}.md` | title, type, slug, status, source, created, updated | Hard constraints |
| Person | `people/{slug}.md` | title, slug, role, org, created, updated | Linked entities and meetings attended |
| Meeting | `docs/meetings/{date-slug}.md` | title, date, source, participants | Backlinks to extracted entities |

## Project Standard

A project should exist when:
1. It has a **distinct deliverable** — something you'd ship, demo, or hand off
2. It **spans multiple sessions** — you'll come back to it repeatedly
3. It typically has its own **codebase or workspace** under `projects/`

The test: would you open a separate Claude session to work on it? If yes → project. If no → its entities belong in the projects it serves.

## Conventions

### Wikilinks
All internal links use Obsidian wikilinks: `[[type/slug|Display Text]]`

Examples:
- `[[decisions/auth-strategy|Auth Strategy Decision]]`
- `[[people/rugved-ambekar|Rugved Ambekar]]`
- `[[docs/meetings/2026-04-07-sync|April 7 Sync]]`
- `[[projects/wa-sales-command/ctx-wa-sales-command|Sales Command Center]]`

### Slugs
Lowercase, kebab-case.
- Action items: `owner-verb-noun` (e.g., `rugved-build-rd-mcp-server`)
- Decisions: `topic-description` (e.g., `azure-cloud-platform`)
- People: `full-name` (e.g., `rugved-ambekar`)

### Frontmatter
Every entity page starts with YAML frontmatter:
```yaml
---
title: "Human-readable title"
type: decisions
slug: kebab-case-slug
status: null
source: "docs/meetings/2026-04-07-sync.md"
created: "2026-04-07"
updated: "2026-04-07"
---
```

### Filing Principle
The vault stores **durable, cross-session-relevant information**. Things that help tomorrow's Claude understand what happened, what was decided, and what needs to happen next. Code-level details live in git. Ephemeral discussion stays in the conversation.

## Auto-Priming

Two mechanisms work together:

1. **Always-loaded rule** (`.claude/rules/context-vault.md`) — Tells Claude the vault exists and how to use it. Loads every session.

2. **Project-scoped rules** (`.claude/rules/project-{slug}.md`) — Each has a `paths:` glob scoped to the project directory. When Claude reads files in that project, the rule loads and tells Claude to read the project context page. This is automatic — no command needed.

The `ctx-prime` skill (model-invocable) supports this by silently loading context at session start.

## Common Workflows

**Starting a focused work session:**
`/ctx:prime wa-sales-command` → full briefing → start working

**After a client meeting:**
`/ctx:ingest --latest` → review entities → approve → vault updated

**Client sends a document:**
`/ctx:catalog ~/Downloads/client-doc.pdf` → categorize → link → filed

**End of a productive session:**
`/ctx:convo` → review what happened → approve vault updates → close session

**Things feel messy:**
`/ctx:maintain` → 5-phase audit → approve fixes → vault cleaned up

**Quick check-in:**
`/ctx:status` → open items, recent activity → decide what to work on

## Obsidian Integration (Optional)

If the `obsidian` plugin is installed, the context system gains enhanced capabilities:

- **Dashboard** (`dashboard.base`) — Live queryable views of action items, decisions, people, and meetings. Auto-updates as entity pages change. Created by `/ctx:init`.
- **Markdown quality** — Entity pages use Obsidian-flavored markdown conventions (callouts, block IDs, embeds) when creating/updating pages via ingest, convo, or ctx-update.
- **Canvas graphs** — `/ctx:prime` can generate visual knowledge graphs for projects as `.canvas` files.
- **Web content** — `/ctx:catalog` uses Defuddle for clean markdown extraction from web pages.

All of these are optional. The system works identically without the obsidian plugin — you just get plain markdown files instead of enhanced Obsidian features.
