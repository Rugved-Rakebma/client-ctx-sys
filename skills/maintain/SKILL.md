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

1. Run `just kb-list` to enumerate all entities.
2. Run targeted `just kb-search` queries to find potential duplicates (similar titles/content).
3. Read entities with `just kb-get` and identify:
   - **Duplicates:** entities covering the same topic.
   - **Contradictions:** entities that disagree with each other.
   - **Miscategorized:** entities filed under the wrong type.
   - **Stale entries:** entities that reference outdated information.
4. Propose changes: merges, deletions, updates.
5. **ALL changes require explicit user approval.** Never auto-apply.
6. On approval, use `just kb-add` to update entities. For deletions, note the entity to remove (direct DB deletion is not yet supported via CLI — flag these for manual removal).

## Important

- This skill is **user-initiated only** — it never runs automatically.
- Present findings as a clear list of proposed actions, not a wall of text.
