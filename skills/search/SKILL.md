---
name: search
description: Search the knowledge base
allowed-tools: Bash, Read
user-invocable: true
disable-model-invocation: false
argument-hint: "<your question>"
---

# KB Search

## Pre-injection

- Run `just kb-status 2>/dev/null`

## Flow

0. **Status-aware shortcut:** If the question is about what's outstanding, open, pending, or incomplete (e.g., "what action items are open?"), skip FTS and run `just kb-list --type action-items --status open` instead. Read and present the results directly.

1. Break the user's question into 2-4 targeted search queries. Don't pass the raw question as one search — decompose it into specific terms and concepts.
   - Example: "What did we decide about auth and why?" → search for "auth", "authentication", "OAuth", "SSO"
2. Run `just kb-search "<query>"` for each targeted query.
3. Read the full content of the top results using `just kb-get "<type>/<slug>"` for any result that looks relevant.
4. Synthesize an answer grounded in KB content. Cite entity references (`type/slug`) for every claim.
5. If the KB doesn't have relevant information, say so plainly: "Nothing in the KB on that topic."

## Also Check

- Read `.knowledge-base/file-manifest.yaml` to see if there are filed documents relevant to the question.
- If a filed document looks relevant, read it with the Read tool for additional context.

## Behavior

- No apologies.
- No suggestions to ingest more content.
- Fast: search, read, answer.
- Cite sources.
- Search results include entity status (open, completed, etc.) — mention it when relevant to the user's question.
