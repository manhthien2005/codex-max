---
name: security-auditor
description: "Optional deep security audit workflow for broader DevSecOps, architecture, compliance, and residual-risk reviews beyond the normal security-review path."
risk: safe
source: codex-max
origin: Antigravity-adapted
date_added: "2026-04-19"
---

# Security Auditor

## Overview

Use `security-auditor` for deeper security work than the standard `security-review` skill.
This skill is appropriate when the task expands from feature-level review into broader audit territory: architecture, pipelines, compliance posture, residual risk, and security control coverage.

This skill is installed as an **optional** library skill, not a core routing default.

## Use when

- Performing a deeper security audit or risk assessment
- Reviewing CI/CD, supply chain, secret handling, or broader DevSecOps posture
- Evaluating compliance-oriented controls
- Prioritizing security findings by severity and business impact
- Checking whether mitigations are complete or residual risk remains

## Do not use when

- The task is only a small risky code change that fits `security-review`
- Intrusive testing is out of scope or not authorized
- The user only needs a lightweight checklist rather than an audit

## Recommended workflow

### 1. Confirm audit scope

Clarify:
- systems and boundaries in scope
- environments that may be touched
- type of review: application, infrastructure, pipeline, compliance, or mixed

### 2. Map the high-risk surface

Inspect:
- auth and authorization boundaries
- secrets handling
- sensitive data flows
- external integrations
- deployment and CI/CD controls
- dependency and supply-chain exposure

### 3. Prioritize findings

Report findings with:
- severity
- business impact
- exploitability or likelihood
- recommended remediation
- residual risk if not fixed

### 4. Validate fixes when possible

If mitigations are applied, confirm whether the original risk is actually reduced.

## Output contract

When this skill is used, the result should include:

- **Scope**
- **High-risk areas inspected**
- **Findings by severity**
- **Mitigations**
- **Residual risk**

## Related skills

- `security-review` — default feature-level security workflow
- `documentation-lookup` — for current security-sensitive framework behavior
- `verification-before-completion` — for evidence-backed claims after fixes
