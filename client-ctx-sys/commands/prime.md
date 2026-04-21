---
description: Deep context assembly — vault + project files + current state
disable-model-invocation: true
argument-hint: "<project|person|topic|meeting>"
---

# Context Prime

Prime the current session with a complete picture. The argument can be anything — a project name, a person, a topic, a meeting date, or a concept.

This is NOT just reading a vault page. Prime assembles context from multiple sources — the vault (compiled knowledge), project files (actual documents), and current state (what's in flight) — into one synthesized briefing.

## Workflow

### 1. Find the context vault

Look for `context-vault/` in the current directory or parent directories (up to 3 levels).

### 2. Determine what to prime on

Parse the argument:

- **Project name** (e.g., "sales-command", "wa-sales-command"): Full project prime (see below)
- **Person name** (e.g., "Kevin", "Reuben"): Person prime
- **Meeting date** (e.g., "april 7", "2026-04-07"): Meeting prime
- **Topic/concept** (e.g., "360dialog", "onboarding", "bigquery"): Topic prime

### 3. Assemble context (multi-layer)

---

#### Project Prime

**Layer 1 — Vault context:**
Read `context-vault/projects/{slug}/ctx-{slug}.md`. Extract:
- Project status and priority
- Key people and their roles
- Open action items (with owners)
- Key decisions and strategies
- Meeting history
- Related projects (upstream/downstream)

**Layer 2 — Project documents:**
Follow wikilinks from the context page to actual project files. Read key documents:
- Architecture docs, specs, vision docs
- Research and reference material
- Any `.rnd/` state (active spec, architecture, build status, decisions)
- Deliverables

Note which docs exist and their relative freshness.

**Layer 3 — Current state:**
Look at the actual project directory (`projects/{slug}/`):
- What files and directories exist? What's the project structure?
- Any recent changes? (check git log if it's a repo, or file modification dates)
- Any `.claude/rules/` specific to this project?
- Any active work in progress?

**Synthesize and present:**
- **What it is** — project summary, goals, key people (from vault)
- **What it contains** — docs, specs, code structure (from project files)
- **Where it's at** — open items, recent activity, what's in flight (from current state + vault)
- **What's next** — upcoming action items, blocking dependencies

---

#### Person Prime

**Layer 1 — Vault:**
Read `context-vault/people/{slug}.md`. Extract role, org, linked entities.

**Layer 2 — Linked entities:**
Read their assigned action items (open ones in full, completed as summary). Read decisions they're involved in. Note meetings attended.

**Layer 3 — Cross-project presence:**
Which project context pages mention this person? What's their role in each?

**Present:** Who they are, what they own, what they're involved in across all projects.

---

#### Meeting Prime

**Layer 1 — Vault:**
Read `context-vault/docs/meetings/{date-slug}.md`. Extract summary, participants, decisions, action items.

**Layer 2 — Linked entities:**
Read the entities that were extracted from this meeting. Check their current status — have action items been completed since? Have decisions been superseded?

**Layer 3 — Context since:**
What's happened since this meeting? Any follow-up meetings? Status changes on items from this meeting?

**Present:** What was discussed, what was decided, what's been done since, what's still open.

---

#### Topic Prime

**Layer 1 — Vault grep:**
Search across the entire vault for the term. Collect matching entities, people, meetings, project context pages.

**Layer 2 — Read top hits:**
Read the most relevant matching files (cap at 10). Understand how the topic connects across entities and projects.

**Present:** Everything the vault knows about this topic, grouped by type (decisions, action-items, projects, people, meetings). Note which projects it touches.

---

### 4. Offer canvas generation (optional)

If priming on a **project** and the `obsidian:json-canvas` skill is available, offer to generate or update a project canvas at `context-vault/projects/{slug}/{slug}-graph.canvas`. The canvas visualizes the project knowledge graph:
- Center node: project context page (file node)
- Connected decision nodes (color 4 — green)
- Connected open action-item nodes (color 1 — red)
- Connected people nodes (color 5 — purple)
- Connected meeting nodes (color 6 — gray)

If the skill is not available, skip this offer entirely.

### 5. Offer to go deeper

After presenting the briefing, ask if the user wants to dive into any specific entity, person, meeting, or document from the results.
