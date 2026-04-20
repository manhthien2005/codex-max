---
name: documentation-lookup
description: "Use current library and framework documentation through Context7 when available, instead of relying on stale assumptions or training data."
risk: safe
source: ECC-adapted
origin: ECC
date_added: "2026-04-19"
---

# Documentation Lookup

## Overview

Use `documentation-lookup` whenever a task depends on accurate, up-to-date behavior of a library, framework, SDK, or API.

In this workspace, the preferred docs source is **Context7** when available.
If Context7 is unavailable, fall back to the best local or official documentation source and state that fallback explicitly.

## Use when

- The user names a framework or library directly
- Code depends on current APIs, setup steps, or config behavior
- A migration or integration needs version-aware guidance
- You need reference examples rather than general memory

## Preferred workflow

### Step 1 — Resolve the library or product

Identify the exact library, framework, or API involved.
If Context7 is available, resolve the correct library identifier first.

### Step 2 — Query the current docs

Fetch only the documentation needed for the task:

- setup/config information
- API/reference information
- version-specific behavior
- code examples that directly answer the question

### Step 3 — Apply the docs carefully

Use the fetched documentation to:

- answer the question
- implement the correct API usage
- explain version-sensitive behavior when relevant

## Output contract

When this skill is used, the result should state:

- **Library / framework**
- **Docs source used** — Context7 or fallback source
- **Relevant current behavior**
- **Implementation guidance** or example

## Rules

- Prefer current docs over memory when the task is library-dependent
- Do not guess API behavior when docs are available
- Do not leak secrets or tokens in doc queries
- If the docs remain ambiguous, state the ambiguity instead of pretending certainty

## Related skills

- `search-first` — use before choosing a new dependency or integration path
- `task-router-lite` — routes into this skill when a task is primarily library/framework/API-driven
