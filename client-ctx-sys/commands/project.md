---
description: Scaffold a new project with context vault overview and auto-prime rule
disable-model-invocation: true
argument-hint: "<project-name>"
---

# Context Project

Create a new project under the client umbrella. Scaffolds the context vault overview page and a path-scoped auto-prime rule.

## Project Standard

A project should exist when:
1. It has a distinct deliverable — something you'd ship, demo, or hand off
2. It spans multiple sessions — you'll come back to it repeatedly
3. It typically has its own codebase or workspace

## Workflow

### 1. Parse argument

Convert the project name to a slug (lowercase, kebab-case). Confirm with user.

### 2. Find the context vault

Look for `context-vault/` in the current directory or parent directories.

### 3. Create the context vault overview

Write `context-vault/projects/{slug}/ctx-{slug}.md`:

```yaml
---
title: "{Project Name}"
status: "New"
priority: medium
---
```

With skeleton sections: Key People, Decisions, Action Items (Open/Completed), Strategies, Meetings, Project Documents, Related Projects.

### 4. Create the auto-prime rule

Write `.claude/rules/project-{slug}.md` at the **client root** (where `.claude/` lives):

```markdown
---
paths:
  - "projects/{slug}/**/*"
---

# Project Context

This project is **{Project Name}**.

At session start, read `context-vault/projects/{slug}/ctx-{slug}.md` for full project context — decisions, action items, key people, meeting history, and project documents.
```

This rule only loads when Claude reads files inside `projects/{slug}/`, keeping it out of context for other projects.

### 5. Create the project directory

Create `projects/{slug}/` if it doesn't exist.

### 6. Update the index

Read `context-vault/index.md`. Add the new project to the Projects table.

### 7. Report

Tell the user what was created:
- Context vault overview path
- Auto-prime rule path (in `.claude/rules/`)
- Project directory path
- Remind them to update the overview as the project evolves
