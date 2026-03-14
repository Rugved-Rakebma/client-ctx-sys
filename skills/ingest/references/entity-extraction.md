# Entity Extraction Guidelines

## Entity Types

Entity types are dynamic — they emerge from content, not a fixed schema. Common types:

### Decisions
- Explicit choices made during a discussion or meeting.
- Always include: rationale, context, who decided, what alternatives were considered.
- Example: "We decided to use OAuth2 for auth because it supports SSO and our enterprise clients require it. JWT-only was considered but rejected due to token revocation complexity."

### Action Items
- Assigned to a specific person.
- Have a clear deliverable.
- May have a deadline.
- Example: "Rugved to draft the API schema by Friday."

### Requirements
- Constraints or needs expressed by stakeholders.
- Distinguish functional vs non-functional.
- Example: "The system must handle 10k concurrent connections (non-functional, performance)."

### Strategies
- High-level approaches, plans, or direction-setting discussions.
- Capture the reasoning behind the strategy, not just the conclusion.

## Rationale Over Facts

Capture WHY something was decided, not just WHAT was decided. The reasoning behind a choice is often more valuable than the choice itself — it tells you when to revisit it.

## Slug Naming

- Lowercase, hyphenated, descriptive.
- Good: `auth-strategy-oauth2`, `api-rate-limit-policy`, `onboarding-flow-redesign`
- Bad: `decision-1`, `item`, `thing-from-meeting`

## Detecting Updates

When an entity covers the same topic as an existing one but reflects evolved understanding:
- Update the existing entity rather than creating a duplicate.
- Preserve the original context and append the new information with a date marker.
- Check `just kb-list --type <type>` to find potential matches before creating new entities.

## Handling Ambiguity

- When unclear if something is a decision or just a discussion, lean toward capturing it. Better to have it than miss it.
- Label confidence when uncertain: mark the entity with a confidence note so future reviews can assess it.
- The `/kb:maintain` skill exists to clean up miscategorized or low-confidence entities later.
