# Runtime Skills Surface

This repository exposes its Codex runtime skills through [`.agents/skills`](./skills).

- `skills/` remains the curated source library, catalog, and maintainer surface.
- `.agents/skills/` is the repo-local runtime mirror used for Codex skill discovery.
- `$HOME/.agents/skills` is synced as a symlink to the repo-local runtime mirror by [`scripts/sync-runtime-skills.sh`](../scripts/sync-runtime-skills.sh).

Use the sync script after changing the curated library so the runtime discovery surface stays aligned.
