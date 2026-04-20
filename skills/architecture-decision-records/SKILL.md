---
name: architecture-decision-records
description: "Use when a significant technical decision should be recorded with context, alternatives, and consequences so the reasoning survives beyond the current session."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Architecture Decision Records

## Overview

Use `architecture-decision-records` when an important technical choice should be captured as an ADR.
The point is not ceremony; the point is preserving why the codebase is shaped the way it is.

## Use when

- A framework, library, pattern, database, or interface style is chosen over an alternative
- The user explicitly asks to record a decision
- A planning/design discussion lands on a significant trade-off
- Future maintainers will likely ask “why did we choose this?”

## ADR model

A good ADR records:

- **Context** — what problem or pressure led to the decision
- **Decision** — what was chosen
- **Alternatives considered** — what else was evaluated and why it was rejected
- **Consequences** — what becomes easier, harder, or riskier because of the choice

## Workflow

### 1. Detect the decision moment

Confirm that the decision is significant enough to record.
Avoid trivial ADRs for minor style or naming choices.

### 2. Gather the decision facts

Capture:

- the motivating context
- the chosen option
- the rejected alternatives
- the rationale and trade-offs
- any follow-up risks or mitigation

### 3. Write or update the ADR artifact

For this workspace, store ADR material under `docs/adr/`.
Use the local template when available:

- `docs/adr/0000-template.md`
- `docs/adr/README.md` as the index

### 4. Keep lifecycle explicit

Possible statuses:

- `proposed`
- `accepted`
- `deprecated`
- `superseded`

## Output contract

When this skill is used, the result should include:

- **Decision title**
- **Context**
- **Decision**
- **Alternatives considered**
- **Consequences**
- **Status**

## Workspace fit

- Prefer short, readable ADRs over long essays
- Record the why more carefully than the what
- If an ADR is created, update the ADR index in `docs/adr/README.md`
- If no ADR artifact should be written yet, still structure the decision in ADR form inside the discussion

## Related skills

- `brainstorming` — use before the decision if the design is still unclear
- `planning-with-files` — use when the decision is part of a longer implementation track
- `task-router-lite` — routes here when the task is primarily about recording a significant choice
