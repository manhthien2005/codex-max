# Skills Library

This directory is the curated **source library** for the workspace skills.

It is no longer the preferred discovery path by itself. Runtime discovery is exposed through:

- repo-local `./.agents/skills`
- user-scope `$HOME/.agents/skills`

Use [`scripts/sync-runtime-skills.sh`](../scripts/sync-runtime-skills.sh) after changing the curated library.

## Source of truth

Two files define the installed surface:

- [`CATALOG.md`](CATALOG.md) — human-readable inventory
- [`manifest.yaml`](manifest.yaml) — machine-readable manifest

## Skill layers

| Layer | Path | Notes |
|---|---|---|
| Runtime and optional skills | `skills/<name>/` | Curated source folders for the runtime mirror |
| Maintainer-only skills | `skills/_maintainers/` | Not part of default routing |
| Internal support assets | `skills/.system/` | Internal/system-facing support only |

## Runtime sync model

The runtime mirror intentionally excludes the catalog and manifest files themselves. It contains only skill directories with `SKILL.md`.

Typical flow:

1. edit or add skills here
2. update `CATALOG.md` and `manifest.yaml`
3. run `bash ../scripts/sync-runtime-skills.sh`
4. verify `.agents/skills` and `$HOME/.agents/skills`
