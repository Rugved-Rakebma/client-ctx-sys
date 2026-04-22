# Client Management Market

Claude Code plugins for client project management — context tracking, meeting ingestion, and persistent knowledge graphs.

## Plugins

| Plugin | Prefix | Description |
|--------|--------|-------------|
| [client-ctx-sys](#client-ctx-sys) | `/ctx:*` | File-first wiki for client context with auto-priming, Fireflies ingestion, and Obsidian-compatible knowledge graph |

```
/plugin marketplace add Rugved-Rakebma/client-mgt-market
/plugin install client-ctx-sys@client-mgt-market
```

---

## client-ctx-sys

### The Problem

Client work compounds context. Every meeting produces decisions, action items, and shifting priorities. Every session needs the full picture — who said what, what was decided, what's still open. Without a system, context lives in your head or scattered across chat logs. Claude starts every session cold.

This plugin adds a persistent context layer. Meetings go in, entities come out, and every future session starts fully primed.

### Quick Start

```
/ctx:init                              # scaffold the context vault + rules
/ctx:project sales-command             # add a project
/ctx:ingest --latest                   # pull latest Fireflies meeting
/ctx:prime sales-command               # deep briefing on a project
```

Run `/ctx:help` for the full reference.

---

### How It Works

The context vault is a markdown wiki at `context-vault/` in the client project root. No database, no CLI — Claude reads and writes files directly.

```
context-vault/
├── index.md                          # Master navigation
├── log.md                            # Chronological ingest history
├── config.yaml                       # Client name, Fireflies config
├── dashboard.base                    # Obsidian live dashboard
├── projects/
│   └── {slug}/ctx-{slug}.md          # Project prime pages
├── decisions/                        # Architectural and strategic choices
├── action-items/                     # Tracked tasks with owner + status
├── strategies/                       # Approach frameworks
├── requirements/                     # Hard constraints
├── people/                           # Participants with linked entities
└── docs/
    ├── meetings/                     # Meeting records with backlinks
    ├── client-docs/                  # Documents from the client
    ├── deliverables/                 # Documents produced for the client
    └── research/                     # Protocol refs, tech evaluations, general research
```

Everything connects via Obsidian-compatible wikilinks: `[[decisions/auth-strategy|Auth Strategy]]`. The vault is a knowledge graph, not a flat folder of notes.

### Auto-Priming

Two mechanisms fire automatically — no commands needed:

1. **Always-loaded rule** (`.claude/rules/context-vault.md`) — tells Claude the vault exists and how to use it. Every session.
2. **Project-scoped rules** (`.claude/rules/project-{slug}.md`) — when Claude opens files in a project directory, the rule fires and loads that project's context page.

Claude starts every session already oriented. The `ctx-prime` skill supports this silently in the background.

### Meeting Ingestion

The primary input pipeline. A single command pulls a Fireflies transcript, extracts entities, and wires them into the knowledge graph:

```
/ctx:ingest https://app.fireflies.ai/view/...
```

What comes out:
- **Decisions** with rationale and source links
- **Action items** with owners and status tracking
- **People pages** with linked entities and meetings attended
- **Meeting record** with backlinks to everything extracted
- **Project context pages** updated with new wikilinks

All changes are proposed and require approval before writing.

---

### Commands

#### Setup
| Command | What It Does |
|---------|-------------|
| `/ctx:init` | Scaffold the vault, install rules, configure statusline. Idempotent. |
| `/ctx:project <name>` | Add a project — vault page + auto-prime rule + directory |

#### Input
| Command | What It Does |
|---------|-------------|
| `/ctx:ingest <url\|--latest>` | Pull a Fireflies meeting, extract entities, update the graph |
| `/ctx:catalog <path>` | File a document into the vault with category and project links |

#### Access
| Command | What It Does |
|---------|-------------|
| `/ctx:prime <target>` | Deep context assembly — project, person, topic, or meeting |
| `/ctx:status` | Quick vault briefing — open items, project inventory, recent activity |

**Prime vs Status:** Status is broad and shallow ("what needs attention across everything?"). Prime is narrow and deep ("tell me everything about THIS").

#### Output
| Command | What It Does |
|---------|-------------|
| `/ctx:convo` | End-of-session capture — file decisions, action items, status changes |

#### Health
| Command | What It Does |
|---------|-------------|
| `/ctx:maintain` | 5-phase vault audit — structure, entities, relationships, archive, report |
| `/ctx:help` | Full system reference |

---

### Skills

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| `init` | `/ctx:init` (user) | Scaffold and configure — includes templates |
| `ctx-prime` | Automatic (model) | Silently load project context at session start |
| `ctx-status` | Automatic (model) | Generate session briefings from vault data |
| `ctx-update` | Automatic (model) | Update vault pages when decisions or action items emerge during work |

Model-invocable skills fire proactively — Claude uses them without being asked when context changes during a session.

---

### Common Workflows

**Starting a focused work session:**
```
/ctx:prime sales-command       # full briefing → start working
```

**After a client meeting:**
```
/ctx:ingest --latest           # pull transcript → review entities → approve
```

**Client sends a document:**
```
/ctx:catalog ~/Downloads/sow.pdf   # categorize → link → filed
```

**End of a productive session:**
```
/ctx:convo                     # capture what happened → approve updates
```

**Things feel messy:**
```
/ctx:maintain                  # 5-phase audit → approve fixes
```

---

### Obsidian Integration

If the `obsidian` plugin is installed, the system gains optional enhancements:

- **Dashboard** — `dashboard.base` provides live queryable views of action items, decisions, people, and meetings
- **Markdown quality** — Entity pages use callouts, block IDs, and embeds
- **Canvas graphs** — `/ctx:prime` can generate visual knowledge graphs as `.canvas` files
- **Web content** — `/ctx:catalog` uses Defuddle for clean markdown extraction from URLs

The system works identically without Obsidian — plain markdown with wikilinks.

---

### Design Principles

1. **File-first.** No database, no state server. Everything is markdown files that Claude reads and writes directly.
2. **Approval before writes.** Every command that modifies the vault proposes changes and waits for explicit approval.
3. **Context compounds.** The vault grows richer with every session. Nothing important is lost between sessions.
4. **Auto-prime, don't ask.** Project context loads automatically via path-scoped rules. No manual priming needed for routine work.
5. **Archive, don't delete.** Completed and superseded items move to archive subdirectories. History is never destroyed.

---

## Repository Structure

```
client-mgt-market/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace definition
└── client-ctx-sys/                   # Plugin: ctx
    ├── .claude-plugin/plugin.json
    ├── CLAUDE.md
    ├── commands/                     # 8 user-invocable commands
    ├── skills/                       # 4 skills (1 user-invocable, 3 model-invocable)
    │   └── init/templates/           # Scaffolding templates for /ctx:init
    └── scripts/                      # Python 3.9 stdlib — statusline, Fireflies
```

## Install

```
/plugin marketplace add Rugved-Rakebma/client-mgt-market
/plugin install client-ctx-sys@client-mgt-market
```

Then in any client project:

```
/ctx:init
```

## Inspiration

This system implements [Andrej Karpathy's LLM Wiki](https://karpathy.ai/blog/llm-wiki) pattern — a persistent, compounding knowledge base where the LLM does all the bookkeeping. Raw sources go in, the LLM extracts entities, maintains cross-references, and keeps the wiki current. Humans curate and direct; the LLM handles the grunt work.

The ctx plugin is a domain-specific instantiation for client project management, with Fireflies meeting transcripts as the primary source pipeline and Obsidian-compatible wikilinks as the graph layer.

## Author

Rugved Ambekar

## License

MIT
