## Knowledge Base

This project has a knowledge base in `.knowledge-base/`. It stores decisions, action items, requirements, and other entities extracted from meetings and documents.

### Quick Reference

- `/kb:search <question>` — search the KB (use this proactively when questions touch project history, decisions, or context)
- `/kb:ingest` — process a Fireflies meeting or document into the KB
- `/kb:status` — show KB stats
- `/kb:catalog` — file a document into docs/ with frontmatter
- `/kb:maintain` — review and clean up duplicates/contradictions

### CLI (via just recipes)

```
just kb-status          # DB stats
just kb-search "query"  # Full-text search
just kb-list            # List all entities
just kb-list --type decisions  # Filter by type
just kb-get "type/slug" # Read one entity
just kb-add '<json>'    # Add entities (used by skills, not directly)
```

### Storage

- **Database is the store.** `knowledge-base.db` holds all entities, people, relations, and FTS index.
- **Docs in `.knowledge-base/docs/`** — filed source documents (meetings, client docs, etc.)
- **`file-manifest.yaml`** — catalog of all filed documents with metadata.
- **No markdown entity files.** Everything is in the DB.
