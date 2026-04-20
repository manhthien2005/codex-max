#!/usr/bin/env bash
# rtk-shell-init.sh — balanced RTK wrappers for Codex Bash calls
# Sourced via BASH_ENV by scripts/launch-codex-rtk.sh

unset BASH_ENV
__rtk="${RTK_BIN:-rtk}"

_rtk_available() {
    command -v "$__rtk" >/dev/null 2>&1
}

_rtk_needs_raw_git() {
    case " $* " in
        *" --porcelain "* | *" -z "* | *" --name-only "* | *" --name-status "* | *" --raw "* | *" rev-parse "* | *" rev-list "* | *" show-ref "* | *" ls-files "* | *" --format="* | *" for-each-ref "*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

git() {
    if ! _rtk_available; then
        command git "$@"
        return
    fi

    if _rtk_needs_raw_git "$@"; then
        command git "$@"
        return
    fi

    case "${1:-}" in
        status | log | diff | show)
            command "$__rtk" git "$@"
            ;;
        *)
            command git "$@"
            ;;
    esac
}

ls() {
    if _rtk_available; then
        command "$__rtk" ls "$@"
    else
        command ls "$@"
    fi
}

cat() {
    if _rtk_available && [ "$#" -eq 1 ] && [ -f "$1" ]; then
        command "$__rtk" read "$1"
    else
        command cat "$@"
    fi
}

pytest() {
    if _rtk_available; then
        command "$__rtk" pytest "$@"
    else
        command pytest "$@"
    fi
}

cargo() {
    if ! _rtk_available; then
        command cargo "$@"
        return
    fi

    case "${1:-}" in
        test | build)
            command "$__rtk" cargo "$@"
            ;;
        *)
            command cargo "$@"
            ;;
    esac
}

docker() {
    if ! _rtk_available; then
        command docker "$@"
        return
    fi

    case "${1:-}" in
        ps | images | logs)
            command "$__rtk" docker "$@"
            ;;
        *)
            command docker "$@"
            ;;
    esac
}
