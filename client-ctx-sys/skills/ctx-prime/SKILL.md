---
name: ctx-prime
description: Load project context from the context vault at session start
allowed-tools: Bash, Read, Glob, Grep
user-invocable: false
---

# Context Prime

Auto-prime Claude with project context. Called proactively at session start when `.claude/rules/` indicates a project context should be loaded.

## Workflow

1. Determine the current project by reading the `.claude/rules/ctx-prime.md` file in the current working directory (if it exists). Extract the project slug and vault path.

2. If no project-level rule exists, look for `context-vault/index.md` in the current directory or parent directories (up to 3 levels).

3. Read the project context page at `context-vault/projects/{slug}/ctx-{slug}.md`:
   - Note the project status and priority
   - Note key people and their roles
   - Scan open action items
   - Note recent meetings

4. Hold this context silently — do not output a briefing unless the user asks. The goal is to be oriented, not to dump information.

## Key Principle

This skill primes context, it does not present it. Claude should be ready to answer project questions immediately after priming, without the user needing to wait for a summary they didn't ask for.
