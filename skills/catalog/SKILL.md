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

1. Read the source file using the Read tool. Determine if it's a **text file** (.md, .txt, .csv, etc.) or a **binary file** (.pdf, .docx, .pptx, .png, .jpg, etc.).
2. Determine the appropriate category for the document (e.g., `meetings`, `client-docs`, `research`, `deliverables`, `internal`).
3. Propose the filing location and approach based on file type.
4. **Wait for user approval.**
5. On approval, file the document (see paths below).
6. Update `.knowledge-base/file-manifest.yaml` with an entry for the filed document.
7. **Check for related action items:**
   - Run `just kb-list --type action-items --status open` to get open action items.
   - If any open action items appear to be fulfilled or addressed by the cataloged document, propose updating their status to `completed`.
   - On approval, write the update JSON to `.knowledge-base/.staging.json` and run `just kb-add .knowledge-base/.staging.json`. Use the `{"entities": [...]}` wrapper format.
8. Confirm what was filed and any action items updated.

### Text files (.md, .txt, etc.)

- Propose location: `.knowledge-base/docs/<category>/<slug>.md`
- Write the document with frontmatter prepended:
  ```yaml
  ---
  title: "Document Title"
  source: "original-filename.ext"
  cataloged: YYYY-MM-DD
  category: <category>
  tags: []
  ---
  ```
- Manifest entry points to the markdown file

### Binary files (.pdf, .docx, .pptx, images, etc.)

- **Copy the original file** into `.knowledge-base/docs/<category>/` preserving its extension:
  `cp "<source-path>" .knowledge-base/docs/<category>/<slug>.<ext>`
- **Write a companion markdown** at `.knowledge-base/docs/<category>/<slug>.md` with frontmatter + a text summary of the document's contents:
  ```yaml
  ---
  title: "Document Title"
  source: "original-filename.ext"
  cataloged: YYYY-MM-DD
  category: <category>
  file: "<slug>.<ext>"
  tags: []
  ---
  ```
  Followed by a summary of the document — key points, what diagrams/images contain, structure overview. This makes the document searchable in the KB.
- Manifest entry includes both paths:
  ```yaml
  - path: docs/<category>/<slug>.md
    file: docs/<category>/<slug>.<ext>
    title: "Document Title"
    category: <category>
    cataloged: YYYY-MM-DD
    source: "original-filename.ext"
  ```

## Important

- Do NOT extract entities — that's `/kb:ingest`'s job. This skill only files documents.
- Preserve the original document content. For text files, only add frontmatter. For binary files, copy as-is.
- If the file is already in `.knowledge-base/docs/`, update the manifest entry if missing but don't duplicate the file.
