---
name: context7-auto-research
description: "Optional alternative docs-current layer that uses Context7-style documentation retrieval automatically for library/framework questions."
risk: safe
source: codex-max
origin: third-party-adapted
date_added: "2026-04-19"
---

# Context7 Auto Research

## Overview

`context7-auto-research` is an optional alternative to the normal `documentation-lookup` flow.
Use it when you specifically want a more automatic Context7-driven docs retrieval mode for library and framework questions.

In this workspace it is **not** a core routing default and should not compete with `documentation-lookup` as a second always-on docs layer.

## Use when

- The task is heavily library/framework dependent
- The user explicitly wants auto-research behavior for docs lookup
- A current-docs answer is needed and the normal docs lookup path is insufficient or too manual

## Rules for this workspace

- Prefer `documentation-lookup` as the canonical docs-current layer in normal routing
- Use this skill only as an optional alternative
- Do not treat both as co-equal core layers at the same time
- Keep queries free of secrets or sensitive data

## Recommended workflow

### 1. Identify the library or framework

State the target technology clearly.

### 2. Fetch current documentation

Use the configured docs-current tooling path to retrieve:
- setup/config guidance
- API behavior
- examples
- version-sensitive notes

### 3. Summarize and apply

Return:
- docs source used
- relevant current behavior
- implementation guidance
- uncertainty if the docs remain ambiguous

## Output contract

When this skill is used, the result should include:

- **Library/framework**
- **Docs source used**
- **Relevant current behavior**
- **Implementation guidance**

## Related skills

- `documentation-lookup` — canonical docs-current layer for the workspace
- `search-first` — dependency choice before implementation
