\
# AGENTS.md

## Repository working contract
- Read this file first, then follow all conventions here before doing anything.
- For complex or long-running tasks, use `PLANS.md` as the planning template via `planning-with-files` skill.
- This workspace is a **multi-repo workspace** — do not assume a single active repo.
- Identify the active repo at the **start of every task** before reading or writing any files.
- Keep scope tight. Read only the files needed for the current task.
- Prefer small, reviewable changes over broad speculative refactors.
- Do not restate the full plan in routine progress updates.

---

## Intelligence Layer Protocol (Session Start)

**At the start of EVERY session, call these in order:**

1. `mempalace_status` — load palace overview (drawers, wings). Restores project context.
2. `semantic://health` — verify Qdrant + Ollama are up before any semantic search.
3. Only after confirming layers are up, proceed to answer the user request.

**Decision tree — which layer to use:**

| Question type | Use this layer |
|:---|:---|
| "What did we decide about X before?" | `mempalace_search` or `mempalace_kg_query` |
| "Where is feature X implemented in the code?" | `semantic://search-code/{query}` |
| "What calls this function / what does this file import?" | GitNexus (`gitnexus` MCP tools) |
| "How does library X work? What's the API?" | `context7` |
| "Find something on the web" | `exa` |
| "What's in this GitHub PR/issue?" | `github` |
| "Scratch notes this session only" | `memory` |

---

## MemPalace (project-level persistent memory)
- v3.3.1 installed. MCP server auto-starts via `run-mempalace-mcp.cmd`.
- **Palace path:** `~/.mempalace/palace` (Windows: `%USERPROFILE%\.mempalace\palace`)
- **Backend:** ChromaDB (HNSW vectors) + SQLite KG (knowledge graph)
- **ONNX model:** `all-MiniLM-L6-v2` (cached at `~/.cache/chroma/`, 166 MB)

**When to use:** Project decisions, architecture notes, context that must survive across sessions.

**Key tools:**
- `mempalace_status` — overview (call ON WAKE-UP, every session)
- `mempalace_search` — semantic search across all drawers
- `mempalace_add_drawer` — save new memory `(wing, room, content)`
- `mempalace_kg_add` — add structured fact `(subject → predicate → object)`
- `mempalace_kg_query` — query facts about an entity before guessing
- `mempalace_diary_write` — record session events (call at session end)
- `mempalace_kg_invalidate` — mark stale fact as no longer true

**Wings configured:** `projects`, `technical`, `decisions`, `debugging`, `architecture`, `context`, `references`

**Protocol:**
- Call `mempalace_status` at session start.
- Before claiming a fact about the project, call `mempalace_search` or `mempalace_kg_query` FIRST.
- After completing a task, call `mempalace_diary_write` to record what happened.
- When architecture decisions are made, call `mempalace_add_drawer` with wing=`decisions`.

---

## Semantic Search (code similarity)
- MCP server `semantic_qdrant_http` auto-starts via `run-semantic-qdrant-stdio.cmd`.
- **Prerequisite:** Qdrant (`http://127.0.0.1:6333`, Docker) + Ollama (`http://127.0.0.1:11434`) must be running.
- **Embedding model:** `qwen3-embedding:0.6b` via Ollama
- **Chunk size:** 40 lines with 10-line overlap

**When to use:** Finding *related* code by concept/intent. NOT for exact symbol lookup.

**Resources:**
- `semantic://health` — check stack before querying (call this first)
- `semantic://search-code/{query}` — search dart code chunks (URL-encode query)
- `semantic://search/{query}` — search all chunk kinds
- `semantic://collection/{name}` — inspect collection point count

**Active collections:**
| Collection | Points | Scope |
|:---|:---:|:---|
| `semantic-health-system-lib` | 1328 | `health_system/lib/**/*.dart` |
| `semantic-health-system` | 72 | health_system (older, smaller) |

**Do NOT** call `qdrant_find` or `qdrant_store` on the upstream `qdrant` server — use `semantic_qdrant_http` resources only.

---

## GitNexus (code graph)
- **Version:** 1.6.1 | **Type:** structural navigation
- **When to use:** Exact symbol lookup, dependency tracing, impact analysis, call graphs.

**Indexed repos (`.gitnexus/` at repo root):**
| Repo | Path | Files | Nodes | Edges |
|:---|:---|:---:|:---:|:---:|
| `health_system` | `D:\DoAn2\VSmartwatch\health_system` | 488 | 2914 | 7216 |
| `Iot_Simulator` | `D:\DoAn2\VSmartwatch\Iot_Simulator` | 158 | 1916 | 5423 |
| `HealthGuard` | `D:\DoAn2\VSmartwatch\HealthGuard` | 167 | 853 | 1764 |
| `healthguard-model-api` | `D:\DoAn2\VSmartwatch\healthguard-model-api` | 90 | 471 | 962 |

**To index a new repo:** `gitnexus index <repo-path>`
**Storage:** `.gitnexus/` at repo root (already in `.gitignore`), `~/.gitnexus/registry.json` globally.

---

## Main Agent Workflow (Task Manager)

The initial Agent acts as a **Task Manager**. Its primary responsibility is to:
1. Call `mempalace_status` + `semantic://health` (Intelligence Layer Protocol above)
2. Identify the active repo and related repos
3. Load the right skills for the task
4. Decide whether to execute directly or spawn subagents

### Two-Phase Skill Strategy

**Phase PLAN — Task Analysis & Briefing**
- ALWAYS load `task-intelligence` skill (`~/.codex/skills/task-intelligence`) first.
- Use it to break down the task, estimate difficulty, map risks, and prepare execution context.
- Do not search for other analysis skills — this is the hardcoded entry point.

**Phase BUILD — Execution Skills Match**
- After analyzing the task, search for the narrowest matching execution skill in `~/.codex/skills/`.
- Match by task domain: e.g. `systematic-debugging` for bugs, `lint-and-validate` for code quality, `planning-with-files` for multi-step work, `verification-before-completion` before closing a task.
- Available skill families:
  - `planning-with-files` — long-running, multi-step, or high-context tasks; keeps state in persistent markdown
  - `task-intelligence` — task breakdown, difficulty rating, risk mapping
  - `systematic-debugging` — structured debugging flow
  - `lint-and-validate` — code quality and validation
  - `verification-before-completion` — gate check before marking task as Done
  - `concise-planning` — lightweight planning for medium tasks
  - Workflow bundles in `skills/workflow_bundles_readme.md` — specialized for frontend, backend, DevOps, security, AI/ML, database, testing, docs
- If creating a subagent: inject the found skills directly into the subagent brief.
- If executing directly: load the skill into the main agent context.
- Do not load many skills at once. Prefer the narrowest relevant skill.

---

## Project detection rules

At the start of every task, identify:
1. **Active repo** — the repo where changes will be made
2. **Related repos** — repos read for context only (no writes)
3. **Allowed write scope** — directories where files can be modified
4. **Git scope** — which repo(s) Git commands may run in

### Known repos in this workspace (examples — not exhaustive)
| Role | Path |
|:---|:---|
| Flutter health app | `D:\DoAn2\VSmartwatch\health_system` |
| IoT simulator | `D:\DoAn2\VSmartwatch\Iot_Simulator` |
| HealthGuard frontend | `D:\DoAn2\VSmartwatch\HealthGuard` |
| AI service | `D:\DoAn2\VSmartwatch\healthguard-ai` |
| Project management | `D:\DoAn2\VSmartwatch\PM_REVIEW` |
| Codex config | `~/.codex` |

> For projects **outside this list**, detect the active repo from the user's working directory or from explicitly mentioned paths. Do not default to any repo.

### Multi-repo rules
- Cross-repo reading is always allowed when context is needed.
- Cross-repo writing requires explicit user approval or a task that explicitly spans multiple repos.
- Never run Git commands in the workspace root `D:\DoAn2\VSmartwatch`.
- Run Git only inside the explicitly declared Git scope repo.

---

## Execution readiness checkpoint

Before starting implementation, present this table explicitly so the user can parse the setup:

| Context Element | Details |
| :--- | :--- |
| **Active repo** | `[path]` |
| **Related repos** | `[paths]` |
| **Context readiness** | `Ready` / `Incomplete` |
| **Execution intent** | `[brief description]` |
| **Difficulty level** | `easy`, `medium`, or `hard` |
| **Subagent decision** | `Spawning Subagent` / `Direct Execution` |
| **Phase BUILD Skills** | `[Skills found/injected for execution]` |

- For `easy` tasks: execute directly, no subagent needed.
- For `medium` tasks: execute directly unless the task has clearly separable phases — then consider spawning.
- For `hard` tasks: **default to spawning at least one subagent**. Only skip if one of these blockers applies:
  - The task requires interactive back-and-forth judgment that only the main agent can handle
  - The task is a single tightly-coupled atomic change with no separable phases
  - State that blocker explicitly if skipping subagent for a hard task.

---

## Hooks & automation

Hooks run automatically — do not re-trigger them manually:

| Hook | When | What it does |
|:---|:---|:---|
| `SessionStart` | Session open / resume | Runs `session-catchup.py` to restore plan context, then `user-prompt-submit.sh` |
| `UserPromptSubmit` | Every user message | Injects plan context into prompt |
| `PreToolUse (Bash)` | Before any Bash tool | Checks plan alignment via `pre_tool_use.py` |
| `PostToolUse (Bash)` | After any Bash tool | Reviews Bash output against plan via `post_tool_use.py` |
| `Stop` | Session end | Runs `stop.py` to save session state |

- Hooks are defined in `~/.codex/hooks.json`
- Hook scripts live in `~/.codex/hooks/`
- If a hook fails silently, it is safe to continue — all hooks use `|| true`

---

## ECC Agents (built-in subagent roles)

These named agents are available for delegation. Use them by naming them in subagent briefs:

| Agent | Config | Strength |
|:---|:---|:---|
| `explorer` | `agents/explorer.toml` | Read-only codebase exploration, tracing execution paths, gathering evidence |
| `reviewer` | `agents/reviewer.toml` | PR review — correctness, security, regressions, missing tests |
| `docs_researcher` | `agents/docs-researcher.toml` | Verify APIs, framework behavior, release notes |

- `explorer` and `reviewer` are `read-only` sandbox — safe to spawn freely for investigation.
- Use `explorer` before making changes when the codebase is unfamiliar.
- Use `reviewer` after changes to gate quality before marking Done.

---

## Subagent policy

- **Spawn freely for `hard` tasks** — this is the default. Do not look for a reason to avoid it.
- Spawn when work is separable: exploration vs. implementation, frontend vs. backend, migration vs. verification.
- **Git Branching Rule:** For `hard` tasks, the subagent MUST checkout a new branch before making changes:
  ```
  git checkout -b agent/<task-name>
  ```
  This keeps main clean if the subagent fails.
- **Fallback & Escalation Policy:** If a subagent fails or its code fails tests **more than 2 times**, it MUST STOP — no infinite fix loops. It must rollback (or delete its branch) and report to the Task Manager.
- Do not pass the full plan to subagents. Give each subagent only:
  - A short scoped task (1–2 lines)
  - Relevant file paths
  - Local constraints
  - Strict output format
  - Injected skills from Phase BUILD

### Worker brief format
```
### Task
[one or two lines]

### Active repo
- [path]

### Related repos for context
- [path]

### Allowed write scope
- [path]

### Git scope
- [repo name / path]

### Files
- [path]

### Injected Skills
- [Skill name or path]

### Do
1. [step]
2. [step]

### Do not
- touch unrelated files
- repeat the full plan
- run Git commands in workspace root

### Output
- Files read
- Files changed
- Result
- Issues
```

---

## MCP servers available

| Server | Type | Purpose |
|:---|:---|:---|
| `mempalace` | command (stdio) | **Project-level persistent memory** — decisions, architecture, context |
| `semantic_qdrant_http` | command (stdio) | Semantic code search via Qdrant + Ollama |
| `gitnexus` | command | Structural code index — symbols, dependencies, blast radius |
| `context7` | HTTP | Up-to-date library/framework documentation |
| `github` | HTTP | GitHub API — PRs, issues, repos |
| `exa` | HTTP | Web search |
| `memory` | command | In-session key-value store (lightweight, resets each session) |
| `playwright` | command | Browser automation and web testing |
| `sequential-thinking` | command | Multi-step reasoning chains |
| `qdrant` (upstream) | command | Raw Qdrant — use only for introspection, not tool calls |

**Usage rules:**
- Use `mempalace` for project-level persistent memory (survives across sessions). Call `mempalace_status` first.
- Use `semantic_qdrant_http` resources for semantic search, NOT `qdrant` tools directly.
- Use `gitnexus` for exact symbol lookup, impact analysis, dependency tracing.
- Use `context7` before writing code that depends on external libraries.
- Use `memory` for lightweight in-session scratch — it resets when the session ends.

---

## Data Storage Map (reference)

| Layer | Data location | Notes |
|:---|:---|:---|
| **Qdrant vectors** | Docker volume `opencode_qdrant_data` → `/qdrant/storage` | Re-index via `index_health_system_repo.py` |
| **GitNexus graph** | `<repo>/.gitnexus/` (per-repo) | 60-66 MB each, add to `.gitignore` |
| **MemPalace drawers** | `~/.mempalace/palace/chroma.sqlite3` | Persistent, survives reboots |
| **MemPalace KG** | `~/.mempalace/palace/knowledge_graph.sqlite3` | SQLite, structured facts |
| **ChromaDB ONNX model** | `~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/` | 166 MB, downloaded once |
| **Ollama embedding** | Ollama data dir | `qwen3-embedding:0.6b`, 0.6 GB |

---

## Planning rules
- If a task is complex (`medium` or `hard`), create or update a `PLANS.md` in the active repo using `planning-with-files` skill.
- Read the full plan once at the start; revisit only when needed.
- Keep the plan as the Task Manager artifact — do not pass it wholesale to subagents.
- Plans must declare:
  - Active repo
  - Related repos (read-only context)
  - Repos allowed to change
  - Repos where Git may run

---

## Verification policy
- Verify changed files first, then expand checks only as needed.
- **Proof required:** "looks good" is not acceptable. Provide concrete proof — actual console output, test pass, API response, or build result.
- If verification is incomplete, state exactly what remains unverified.
- Run verification only inside the declared active repo or allowed write-scope repos.

---

## Reporting format

### Progress update
- Current step + reason
- Done / Remaining
- Context readiness + Difficulty
- Subagent decision
- Active repo / Related repos used

### Final report
- Files modified
- Verification results (with concrete proof)
- Open issues
- Suggested next step
