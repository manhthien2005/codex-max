#!/usr/bin/env bash
# sync-runtime-skills.sh — expose curated skills through .agents/skills and $HOME/.agents/skills
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SOURCE_ROOT="$REPO_ROOT/skills"
REPO_RUNTIME_ROOT="$REPO_ROOT/.agents/skills"
USER_RUNTIME_ROOT="${HOME:-/home/$(id -un)}/.agents/skills"

link_skill_dir() {
    local source_dir="$1"
    local target_dir="$2"
    local relative_target="$3"

    mkdir -p "$target_dir"
    find "$source_dir" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
        if [ -f "$dir/SKILL.md" ]; then
            ln -sfn "$relative_target/$(basename "$dir")" "$target_dir/$(basename "$dir")"
        fi
    done
}

rm -rf "$REPO_RUNTIME_ROOT"
mkdir -p "$REPO_RUNTIME_ROOT" "$REPO_ROOT/.agents"

link_skill_dir "$SOURCE_ROOT" "$REPO_RUNTIME_ROOT" "../../skills"

mkdir -p "$REPO_RUNTIME_ROOT/_maintainers"
link_skill_dir "$SOURCE_ROOT/_maintainers" "$REPO_RUNTIME_ROOT/_maintainers" "../../../skills/_maintainers"

mkdir -p "$REPO_RUNTIME_ROOT/.system"
link_skill_dir "$SOURCE_ROOT/.system" "$REPO_RUNTIME_ROOT/.system" "../../../skills/.system"

mkdir -p "$(dirname "$USER_RUNTIME_ROOT")"
rm -rf "$USER_RUNTIME_ROOT"
ln -sfn "$REPO_RUNTIME_ROOT" "$USER_RUNTIME_ROOT"

printf 'Repo runtime skills: %s\n' "$REPO_RUNTIME_ROOT"
printf 'User runtime skills: %s -> %s\n' "$USER_RUNTIME_ROOT" "$(readlink "$USER_RUNTIME_ROOT")"
