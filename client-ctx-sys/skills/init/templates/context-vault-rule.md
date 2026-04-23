---
---

# Context Vault

This project has a context vault at `context-vault/`.

When asked about project history, decisions, people, or context — check `context-vault/index.md` for navigation, then read relevant entity pages.

When creating documents, specs, or deliverables for a project:
1. Link the document from the project's overview page in `context-vault/projects/`
2. If the work introduces decisions or action items, create entity pages in `context-vault/`
3. Update the project overview with new wikilinks

When decisions are made during a session — create `context-vault/decisions/{slug}.md` and add a wikilink to the relevant project overview.

ALL links in vault pages use Obsidian wikilinks — never raw file paths. This applies to vault entities AND project files outside the vault: `[[path/to/file|Display Text]]`

## Corrections

If `context-vault/ctx-corrections.md` exists, read it at session start. It contains past mistakes and corrections related to the context system in this project — follow them to avoid repeating errors.

When the user corrects a mistake you made related to the context vault (wrong file placement, broken links, incorrect conventions, etc.), append the correction to `context-vault/ctx-corrections.md` with a date and brief description of what went wrong and the correct approach.
