---
name: git-workflow
description: "Use for branching, commit, PR, merge, rebase, and release discipline. Adapts Git workflow guidance to codex-max multi-repo boundaries."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Git Workflow

## Overview

Use `git-workflow` when the task is mainly about git process rather than code behavior.
Examples: branching strategy, commit style, PR hygiene, merge/rebase choice, release steps, or conflict-handling discipline.

## Workspace-specific rules

This workspace is multi-repo. Therefore:

- Always identify the active repo first
- Run git commands only inside the declared git scope repo
- Never run git commands in the workspace root unless that root is explicitly the active repo
- Keep branch and PR guidance aligned with the repo actually being changed

## Use when

- Setting up or enforcing branch conventions
- Deciding merge vs rebase
- Writing commit messages or PR descriptions
- Preparing releases or tags
- Explaining or improving repo collaboration discipline
- Resolving git-process confusion in a multi-repo environment

## Core guidance

### Branching

Prefer a simple, reviewable workflow unless the repo clearly needs something more complex.
Short-lived branches are usually the best default.

### Commit messages

Prefer clear, scoped commit messages that explain the intent of the change.
A conventional-commit style is acceptable when the repo already uses it.

### Merge vs rebase

- Rebase is useful for keeping a local feature branch current before review
- Merge is safer when preserving shared branch history matters
- Avoid rewriting history on shared/protected branches

### Pull requests

A good PR should state:

- what changed
- why it changed
- how it was verified
- what risks or follow-up work remain

## Output contract

When this skill is used, the result should include:

- **Active git scope**
- **Recommended branch strategy**
- **Commit/PR guidance**
- **Merge/rebase recommendation**
- **Release or rollback notes** if relevant

## Related skills

- `verification-before-completion` — ensure evidence exists before calling work ready
- `planning-with-files` — when git workflow is part of a larger multi-step task
- `task-router-lite` — routes here when git process is the main subject
