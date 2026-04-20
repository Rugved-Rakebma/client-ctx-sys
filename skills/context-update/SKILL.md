---
name: context-update
description: Update context vault pages after changes during a session
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
user-invocable: false
---

# Context Update

Update the context vault after changes occur during a session — new decisions, action items, documents, or status changes. Called proactively by Claude when significant changes happen.

## When to Trigger

- A decision is made during a session → create entity page + update project overview
- An action item is identified → create entity page + update project overview
- A document or spec is created → link from project overview
- An action item is completed or status changes → update the entity page

## Entity Page Format

### Decision
```yaml
---
title: "Decision title"
type: decisions
slug: kebab-case-slug
status: null
source: "docs/meetings/YYYY-MM-DD-slug.md"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

Rationale and context for the decision.
```

### Action Item
```yaml
---
title: "Owner: Task description"
type: action-items
slug: owner-slug-task-description
status: "open"
source: "docs/meetings/YYYY-MM-DD-slug.md"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

Details, context, deliverable.
```

### Person
```yaml
---
title: "Full Name"
slug: full-name-slug
role: "Role"
org: "Organization"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---
```

## Wikilink Convention

All internal links use Obsidian wikilinks: `[[type/slug|Display Text]]`

- Entity to person: `[[people/rugved-ambekar|Rugved Ambekar]]`
- Entity to meeting: `[[docs/meetings/2026-04-07-sync|Meeting Title]]`
- Entity to entity: `[[decisions/some-decision|Decision Title]]`

## Update Steps

1. Write the new entity page in the correct directory. Use Obsidian-flavored markdown conventions (`obsidian:obsidian-markdown` skill) if available; standard markdown with `[[wikilink]]` syntax otherwise.
2. Read the relevant project context page (`context-vault/projects/{project}/ctx-{project}.md`)
3. Add the new entity as a wikilink in the appropriate section (Decisions, Action Items, etc.)
4. If a new person is referenced, check if `context-vault/people/{slug}.md` exists — create if not
5. Update `context-vault/index.md` if the entity type section needs a new row

## Hard Rules

1. **Never delete entity pages** — mark as superseded or completed, don't remove
2. **Always use wikilinks** — every entity page must link to its source and related entities
3. **Slug convention** — lowercase, kebab-case. Action items: `owner-verb-noun`. Decisions: `topic-description`.
