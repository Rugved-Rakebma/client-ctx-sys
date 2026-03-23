---
name: maintain
description: Review and clean up the knowledge base
allowed-tools: Bash, Read, Write
user-invocable: true
disable-model-invocation: true
---

# KB Maintain

## Pre-injection

- Run `just kb-status 2>/dev/null`

## Flow

### Phase 1: Status Triage

1. Run `just kb-list --type action-items` to find all action items.
2. Identify action items with no status (NULL — pre-migration entities).
3. Read each with `just kb-get` and propose setting status to `open` or `completed` based on content.
4. Also check if any `open` action items should be closed, or any `completed` ones should be reopened.
5. **ALL status changes require explicit user approval.**
6. On approval, write the JSON to `.knowledge-base/.staging.json` and run `just kb-add .knowledge-base/.staging.json`.

### Phase 2: Cleanup

1. Run `just kb-list` to enumerate all entities.
2. Run targeted `just kb-search` queries to find potential duplicates (similar titles/content).
3. Read entities with `just kb-get` and identify:
   - **Duplicates:** entities covering the same topic.
   - **Contradictions:** entities that disagree with each other.
   - **Miscategorized:** entities filed under the wrong type.
   - **Stale entries:** entities that reference outdated information.
4. Propose changes: merges, deletions, updates.
5. **ALL changes require explicit user approval.** Never auto-apply.
6. On approval, write the JSON to `.knowledge-base/.staging.json` and run `just kb-add .knowledge-base/.staging.json`. For deletions, note the entity to remove (direct DB deletion is not yet supported via CLI — flag these for manual removal).

## Writing to kb-add

**NEVER pass JSON inline on the command line.** Always use the staging file:

1. Write JSON to `.knowledge-base/.staging.json` using the Write tool
2. Run `just kb-add .knowledge-base/.staging.json`
3. The CLI clears the file automatically after a successful write

The JSON must use the `{"entities": [...]}` wrapper:
```json
{
  "entities": [
    {"type": "action-items", "slug": "my-slug", "title": "Title", "content": "Content", "status": "open"}
  ]
}
```

## Important

- This skill is **user-initiated only** — it never runs automatically.
- Present findings as a clear list of proposed actions, not a wall of text.
