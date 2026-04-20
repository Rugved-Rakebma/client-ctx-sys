---
description: End-of-session context capture — ensure nothing important is lost
disable-model-invocation: true
---

# Context Convo

End-of-session context capture. Reviews what happened during the session and ensures all durable, cross-session-relevant information is properly filed in the context vault. Run this before closing a session.

## Step 1: Review the session

Understand the session's scope:
- What was discussed? Which project(s) were touched?
- What kind of session was this? (build session, meeting prep, client discussion, research, planning, debugging, design review, etc.)
- What was the working scope? (single project, multiple projects, client-wide)

Read the conversation history to identify what happened.

## Step 2: Extract vault-worthy items

Only durable, cross-session-relevant information belongs in the vault. Identify:

**Create or update:**
- Decisions made during the session (explicit or implicit — "we decided to use X" or "we're going with approach Y")
- New action items identified (who needs to do what)
- Action items completed or status changed (resolved during this session)
- Strategy shifts or new requirements discovered
- People updates (new collaborators introduced, role changes, org changes)
- Documents created during the session that should be linked from project context pages
- Corrections to existing vault content (wrong information discovered, stale data that needs updating)

**NOT vault-worthy — do not file:**
- Temporary debugging steps and findings (ephemeral)
- Code-level implementation details (these live in git)
- Conversation-specific discussion that doesn't carry forward
- Things already captured by other commands run during the session (e.g., if `/ctx:ingest` already ran, don't re-file those entities)

## Step 3: Check existing vault state

Before proposing changes:
- Read the relevant project context page(s) to understand what's already there
- Grep entity directories for potential duplicates of what you're about to propose
- Check if any proposed action items or decisions already exist (update them, don't create duplicates)

## Step 4: Propose updates

Present ONE consolidated list of all proposed changes:

- **Entity pages to create** — type, slug, title, content preview, project assignment
- **Entity pages to update** — what's changing and why (e.g., "status: open → completed", "added new context from today's discussion")
- **Project context page links to add** — which entities are being added to which project's context page
- **People page updates** — new action items, meetings, role changes
- **Index/log updates** — new entries needed

For each item, explain briefly WHY it's vault-worthy (what makes it durable and cross-session-relevant).

**Wait for explicit approval before writing anything.**

## Step 5: Apply (on approval)

Write all changes:
1. Create new entity pages with proper frontmatter and wikilinks. Use Obsidian-flavored markdown conventions (`obsidian:obsidian-markdown` skill) if available; standard markdown with `[[wikilink]]` syntax otherwise.
2. Update existing entity pages (preserve existing content, add new context)
3. Update project context pages — add new wikilinks in correct sections
4. Update people pages if needed
5. Update `context-vault/index.md` with new entries
6. Append to `context-vault/log.md` if a significant source was processed

All entities must have:
- Complete YAML frontmatter (title, type, slug, status, source, created, updated)
- Obsidian wikilinks to source, assignees, and related entities
- Assignment to at least one project context page

## Step 6: Confirm

Report what was captured:
- N entities created, N updated
- Project context pages modified
- People pages modified
- Any corrections applied to existing vault content

Confirm the vault is current. The user can close the session knowing nothing important is lost and the next session will start fully primed.

## Key Principles

1. **Understand the session type** — a build session produces different vault items than meeting prep or a client discussion
2. **Update, don't duplicate** — always check for existing entities before creating new ones
3. **Be selective** — only file what matters across sessions. If it won't help tomorrow's Claude, don't file it.
4. **Preserve context** — when updating an entity, add to the existing content rather than replacing it. The history of how a decision evolved is valuable.
5. **The goal** — tomorrow's session starts fully primed with today's learnings
