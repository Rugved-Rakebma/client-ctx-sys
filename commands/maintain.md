---
description: Comprehensive context vault maintenance — structural audit, entity health, relationship integrity, and archive cleanup
disable-model-invocation: true
---

# Context Maintain

Full maintenance pass on the client context vault. Runs in interactive phases — present findings after each phase, wait for user direction before proceeding. This command keeps the entire client umbrella clean and consistent.

## Phase 1: Structural Audit

Verify alignment between the filesystem and the context vault.

### 1a. Project ↔ Directory alignment

- List all directories in `projects/` (physical project dirs)
- List all directories in `context-vault/projects/` (vault project entries)
- **Flag mismatches:**
  - Physical project dir exists but no vault entry → "Untracked project"
  - Vault entry exists but no physical dir → "Phantom project"
  - Naming inconsistencies between physical dir and vault slug

### 1b. Rule file validity

- For each `.claude/rules/project-*.md`, verify:
  - The `paths:` glob points to a directory that actually exists
  - The context page path referenced in the rule body exists
- Flag rules pointing to nonexistent paths

### 1c. Naming consistency

- Check that vault project slugs match their physical directory names exactly
- Check that context page files exist in each vault project directory
- Flag misspellings or mismatches

### 1d. Stale tooling references

- Check for old justfile with KB CLI recipes
- Check settings for old `kb-*` or `k-base:*` permissions
- Check config.yaml for old system references
- Check CLAUDE.md for outdated sections
- Check Obsidian workspace files for old paths

**Present Phase 1 findings. Wait for user direction.**

---

## Phase 2: Entity Health

Audit all entity pages for completeness and issues.

### 2a. Orphan entities

Scan all entity files in `decisions/`, `action-items/`, `strategies/`, `requirements/`. For each, check if it's linked from ANY project context page in `context-vault/projects/`.

Report unlinked entities — these need to be assigned to a project or flagged for removal.

### 2b. Duplicate entities

- Scan for entities with very similar titles or slugs across types
- Check for the same concept captured as both a decision and a strategy
- Check `context-vault/people/` for duplicate people (similar names, same first name with different slugs, `alias_of` redirect stubs that should have been cleaned up)

### 2c. Stale action items

Find open action items where `created` date is older than 14 days:
- Propose status update: completed? still open? superseded?
- Group by owner for easier review

### 2d. Missing frontmatter

Check every entity page for required frontmatter fields:
- `title`, `type`, `slug` — required on all entities
- `status` — required on action-items
- `source` — should exist (null is OK but flag for review)
- `created`, `updated` — should exist

### 2e. Empty or minimal content

Flag entity pages where the body content is empty or under 20 characters — these are stubs that need filling or removing.

**Present Phase 2 findings. Wait for user direction.**

---

## Phase 3: Relationship Integrity

Verify all connections in the knowledge graph.

### 3a. Broken wikilinks

Extract all `[[...]]` patterns from every `.md` file in the vault. Check that each target file exists. Report broken links with the source file.

### 3b. Missing bidirectional links

For each entity page:
- Has a `source` in frontmatter → does that meeting doc link back to this entity?
- Is an action item → does it have an assignee wikilink to a person page?
- Is linked from a meeting → does the meeting's Knowledge Graph section include it?

For each person page:
- Are all their assigned action items listed?
- Are all meetings they attended listed?

### 3c. Cross-project relationships

For each project context page, check the "Related Projects" section:
- Are upstream/downstream dependencies documented?
- Do related projects link back?
- Are there entities shared across projects that should be cross-referenced?

### 3d. People ↔ entity consistency

- Are all action-item slug owners (first name prefix) tracked as people pages?
- Are meeting participants all tracked as people pages?
- Flag people referenced in entity content but missing from `context-vault/people/`

**Present Phase 3 findings. Wait for user direction.**

---

## Phase 4: Archive & Cleanup

Keep the active context lean. Move completed/superseded items out of the hot path.

### 4a. Close completed action items

- Collect all action items with `status: "completed"`
- Create `context-vault/action-items/closed/` if it doesn't exist
- Move completed files to `action-items/closed/` — files keep their full content, frontmatter, and wikilinks intact
- Wikilinks from project context pages still resolve (Obsidian finds files regardless of subdirectory)
- No content rewriting needed
- `dashboard.base` views auto-update — filters exclude `closed/` subfolders, so no manual index rebuild needed for Obsidian users

### 4b. Close superseded decisions

- Find decisions whose content mentions "superseded", "replaced by", or are marked superseded in project context pages
- Create `context-vault/decisions/closed/` if it doesn't exist
- Move superseded files to `decisions/closed/` — same approach as action items

### 4c. Clean redirect stubs

Find any people pages with `alias_of` frontmatter. If the canonical page exists and is healthy, delete the redirect stub.

### 4d. Rebuild index.md

After all archival:
- Regenerate entity counts (excluding archived items)
- Ensure the Projects table is current
- Remove archived entities from type tables
- Add an Archive section at the bottom linking to archive files

**Present Phase 4 proposals. Wait for explicit approval before archiving anything.**

---

## Phase 5: Report

Summary of everything done:
- Structural issues found and fixed
- Entities audited (orphans resolved, duplicates merged)
- Relationships repaired (broken links fixed, backlinks added)
- Items archived (N completed actions, N superseded decisions)
- Current vault health: entity counts by type, project count, people count

---

## Hard Rules

1. **Never delete without approval** — always present and wait
2. **Archive, don't destroy** — completed/superseded items go to archive files, not deleted without record
3. **Fix links before archiving** — ensure all cross-references are valid before moving things
4. **One phase at a time** — don't run Phase 3 until Phase 2 is resolved
5. **Report honestly** — if the vault is clean, say so. Don't invent issues.
