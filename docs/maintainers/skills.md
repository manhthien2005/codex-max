# Maintainer Guide: Skills Library and Runtime Surface

This repository now separates the curated skill library from the runtime discovery surface.

## Layers

| Layer | Path | Purpose |
|---|---|---|
| Curated source library | `skills/` | Skill content, catalog, manifest, maintainer material |
| Repo-local runtime surface | `.agents/skills/` | What Codex discovers from this repo |
| User-scope runtime surface | `$HOME/.agents/skills` | Global skill discovery across repos |
| Maintainer-only skills | `skills/_maintainers/` | Curation workflows, not default routing |

## Required updates

When you add or restructure a skill:

1. update `skills/CATALOG.md`
2. update `skills/manifest.yaml`
3. update `skills/README.md` if the visible surface changed
4. run `bash scripts/sync-runtime-skills.sh`
5. verify that `.agents/skills/` and `$HOME/.agents/skills` still resolve correctly

## Verification baseline

Typical verification for the skills surface now includes:

- `bash scripts/sync-runtime-skills.sh`
- `test -L .agents/skills/<skill-name>` or `find .agents/skills -maxdepth 2 -name SKILL.md`
- content checks for `skills/CATALOG.md` and `skills/manifest.yaml`

The runtime surface is symlink-based by design because this workspace now targets WSL/Linux as the primary runtime.
