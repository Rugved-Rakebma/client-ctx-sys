---
description: File a document into the context vault with links
disable-model-invocation: true
argument-hint: "<file-path>"
---

# Context Catalog

File a document into the context vault with proper frontmatter and wikilinks to relevant project overviews.

## Workflow

### 1. Read the source document

If the argument is a URL (starts with `http`):
- Use the `obsidian:defuddle` skill to extract clean markdown if available
- Otherwise use WebFetch to read the page content
- Proceed with the extracted content as the document to catalog

If the argument is a file path, read the file directly.

Determine its nature:
- Client document (sent by client, external)
- Deliverable (produced by us for the client)
- Research (technical research, reference material)

### 2. Determine filing location

| Category | Location |
|----------|----------|
| Client docs | `context-vault/docs/client-docs/{slug}.md` |
| Deliverables | `context-vault/docs/deliverables/{slug}.md` |
| Research | `context-vault/docs/research/{slug}.md` |

### 3. Propose filing

Present: category, destination path, frontmatter, which project overview(s) to link from. Wait for approval.

### 4. File the document (on approval)

**Text files (.md, .txt):** Write to destination with frontmatter (title, source, cataloged date, category, tags) followed by content.

**Binary files (.pdf, .docx, images):** Copy original to destination. Write a markdown companion with frontmatter + text summary.

### 5. Link from project overviews

Add the document as a wikilink in the Project Documents section of relevant overview(s).

### 6. Report

Confirm what was filed and where it was linked.

## Hard Rules

1. Do NOT extract entities — that's `/ctx:ingest`'s job
2. Always ask for approval before writing
3. Always link from at least one project overview
