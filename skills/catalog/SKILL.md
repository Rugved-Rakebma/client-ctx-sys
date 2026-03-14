---
name: catalog
description: File a document into the KB docs directory with frontmatter
allowed-tools: Bash, Read, Write, Edit
user-invocable: true
disable-model-invocation: true
argument-hint: "<file-path>"
---

# KB Catalog

File a document into `.knowledge-base/docs/` with proper frontmatter and update the file manifest.

## Flow

1. Read the source file using the Read tool.
2. Determine the appropriate category for the document (e.g., `meetings`, `client-docs`, `research`, `deliverables`, `internal`).
3. Propose the filing location: `.knowledge-base/docs/<category>/<slug>.md`
4. Propose frontmatter:
   ```yaml
   ---
   title: "Document Title"
   source: "original-filename.ext"
   cataloged: YYYY-MM-DD
   category: <category>
   tags: []
   ---
   ```
5. **Wait for user approval.**
6. On approval:
   - Write the document to the proposed location with frontmatter prepended.
   - Update `.knowledge-base/file-manifest.yaml` — add an entry:
     ```yaml
     - path: docs/<category>/<slug>.md
       title: "Document Title"
       category: <category>
       cataloged: YYYY-MM-DD
       source: "original-filename.ext"
     ```
7. Confirm what was filed and where.

## Important

- Do NOT extract entities — that's `/kb:ingest`'s job. This skill only files documents.
- Preserve the original document content. Only add frontmatter.
- If the file is already in `.knowledge-base/docs/`, update the manifest entry if missing but don't duplicate the file.
