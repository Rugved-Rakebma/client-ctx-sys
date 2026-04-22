## Context Vault

Client context system at `context-vault/`. Markdown wiki with Obsidian-compatible wikilinks — no database, no CLI.

### Structure
- `context-vault/index.md` — Master navigation
- `context-vault/projects/{slug}/ctx-{slug}.md` — Project prime pages
- `context-vault/decisions/`, `action-items/`, `strategies/`, `requirements/`, `people/` — Entity pages
- `context-vault/docs/meetings/` — Meeting records with backlinks
- `context-vault/docs/research/` — Protocol references, tech evaluations, general research (filed via `/ctx:catalog`)

### Priming
Read `context-vault/index.md` to orient. When a user mentions a project, read its overview. Project overviews link to all relevant entities, people, meetings, and project documents.

### During Work
- Decisions made → create `context-vault/decisions/{slug}.md`, add wikilink to project overview
- Action items identified → create `context-vault/action-items/{slug}.md` with owner + status
- Documents created → link from relevant project overview
- All internal links use Obsidian wikilinks: `[[type/slug|Display Text]]`

### Entity Frontmatter
All entity pages use YAML frontmatter with: title, type, slug, status (for action-items), source, created, updated.

### Commands
`/ctx:prime`, `/ctx:project`, `/ctx:ingest`, `/ctx:status`, `/ctx:maintain`, `/ctx:catalog`
