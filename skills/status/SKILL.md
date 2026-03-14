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

1. Present a clean, factual summary from the `kb-status` JSON output:
   - Entity counts by type
   - People tracked
   - Sources ingested
   - Relations count
   - DB size
2. No staleness warnings. No suggestions. No nagging. Just facts.
