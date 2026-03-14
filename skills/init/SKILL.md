---
name: init
description: Initialize a knowledge base in the current project
allowed-tools: Bash, Read, Write, Edit
user-invocable: true
disable-model-invocation: true
---

# KB Init

This is the ONE skill that calls `python3 ~/Code/knowledge-base/cli/kb.py init` directly, since `just` recipes don't exist yet in the target project.

## Flow

1. Run `python3 ~/Code/knowledge-base/cli/kb.py init` with optional `--project-name` argument.
2. Ask the user for the project name if not provided.
3. Update `.knowledge-base/config.yaml` with the project name.
4. Check if a `justfile` exists in the project root:
   - If **yes**: check if KB recipes already exist. If not, append the contents of `~/Code/knowledge-base/templates/justfile.snippet` to the end of the existing justfile.
   - If **no**: create a new `justfile` with the snippet contents.
5. Check if a `CLAUDE.md` exists in the project root:
   - If **yes**: append the contents of `~/Code/knowledge-base/templates/claude-kb-section.md` to the end of the existing CLAUDE.md (under a separator).
   - If **no**: create a new `CLAUDE.md` with the KB section contents.
6. Confirm setup is complete. Suggest the user try `/kb:ingest` next.

## Important

- This skill is **idempotent** — safe to re-run. Re-running will not destroy existing data or duplicate justfile recipes.
- If `.knowledge-base/` already exists, skip the init command and just verify/update config, justfile recipes, and CLAUDE.md section.
- Check for existing KB recipes in the justfile before appending (look for `kb_cli` or `kb-init` to detect).
- Check for existing KB section in CLAUDE.md before appending (look for `## Knowledge Base` to detect).
