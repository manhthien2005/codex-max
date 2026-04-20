---
name: security-review
description: "Use when working with authentication, authorization, secrets, sensitive input, file uploads, new endpoints, or any feature with meaningful security risk."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Security Review

## Overview

Use `security-review` to apply a focused security checklist before or during implementation of risky changes.
This skill is for practical review of likely vulnerabilities, not for abstract ritual.

## Use when

- Implementing authentication or authorization
- Handling user input, uploads, or external callbacks
- Creating new API endpoints
- Working with secrets or credentials
- Storing or transmitting sensitive data
- Integrating third-party APIs with privileged access
- Reviewing risky changes before completion

## Security areas to check

### Secrets management

- no hardcoded secrets
- environment-based secret loading
- no sensitive tokens committed to source

### Input validation

- validate user input explicitly
- validate file size/type/shape for uploads
- prefer schema validation and allow-lists

### Query safety

- no unsafe query string concatenation
- parameterized queries or safe ORM usage

### Auth and authorization

- verify both authentication and authorization
- check role/scope before sensitive operations
- review token/session storage and boundary assumptions

### Client-side safety

- avoid unsafe rendering of untrusted content
- sanitize rich content when needed
- check CSRF/XSS implications where relevant

### Sensitive operations

- review logging for secret leakage
- review error messages for information disclosure
- check third-party integration boundaries and permission scope

## Output contract

When this skill is used, the result should include:

- **Security-sensitive surface**
- **Key risks found or checked**
- **Mitigations present or required**
- **Open risks**

## Workspace fit

- Use this as a library skill for risky work, not as an always-on blocker for every task
- Pair with `verification-before-completion` before claiming a risky change is ready
- Keep findings concrete and actionable

## Related skills

- `documentation-lookup` — use for current security-sensitive framework behavior
- `gateguard` — force fact gathering before risky Bash actions
- `verification-before-completion` — require evidence before completion claims on sensitive work
- `task-router-lite` — routes here when the task involves auth, secrets, endpoints, or sensitive data
