---
name: status
description: Show knowledge base contents and stats
allowed-tools: Bash, Read
user-invocable: true
disable-model-invocation: true
---

# KB Status

## Pre-injection

Run `just kb-status 2>/dev/null || echo '{"error": "KB not initialized"}'`

## Behavior

You are producing a **session briefing** — the user's starting point for what to work on. Read the JSON output and present it in this order:

1. **Needs attention** — If there are open action items, lead with them. For each one, state the title, who owns it (if known), and how old it is (compute from `created` date). If there are untriaged items (pre-migration, no status set), flag them: "X action items need triage — run `/kb:maintain` to set their status." If nothing needs attention, say so briefly.

2. **Last activity** — Mention the last source ingested (title, type, date) and the most recently updated entities. This tells the user where they left off.

3. **Inventory** — Entity counts by type, people count, source count, DB size. Keep this compact — a single short paragraph or small table, not a field-by-field dump.

Do not suggest next steps beyond the maintain triage prompt. Do not apologize. Do not recommend ingesting more content. Present the briefing and stop.
