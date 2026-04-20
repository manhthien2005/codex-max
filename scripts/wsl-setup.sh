#!/usr/bin/env bash
# =============================================================================
# wsl-setup.sh — One-time setup: codex CLI + RTK trong WSL Ubuntu
# Run: wsl -d Ubuntu -- bash /mnt/c/Users/MrThien/.codex/scripts/wsl-setup.sh
# =============================================================================
set -euo pipefail

# Fix HOME bị inherit từ Windows env
export HOME="/home/mrthien"
cd "$HOME"

echo "=== [1/6] Fix WSL HOME env ==="
# Ghi vào .bash_profile để đảm bảo mọi session sau đều dùng đúng HOME
BASH_PROFILE="$HOME/.bash_profile"
if ! grep -q "export HOME=/home/mrthien" "$BASH_PROFILE" 2>/dev/null; then
    echo 'export HOME=/home/mrthien' >> "$BASH_PROFILE"
    echo "  Added HOME fix to $BASH_PROFILE"
else
    echo "  HOME fix already in $BASH_PROFILE"
fi
# Cũng fix .bashrc cho interactive shells
BASHRC="$HOME/.bashrc"
if ! grep -q "export HOME=/home/mrthien" "$BASHRC" 2>/dev/null; then
    sed -i '1s/^/export HOME=\/home\/mrthien\n/' "$BASHRC"
    echo "  Added HOME fix to $BASHRC"
fi

echo ""
echo "=== [2/6] Symlink ~/.codex → Windows .codex ==="
CODEX_WIN="/mnt/c/Users/MrThien/.codex"
CODEX_LNK="$HOME/.codex"
if [ -L "$CODEX_LNK" ]; then
    echo "  Symlink already exists: $CODEX_LNK → $(readlink $CODEX_LNK)"
elif [ -d "$CODEX_LNK" ]; then
    echo "  WARNING: $CODEX_LNK is a real directory, not a symlink!"
    echo "  Rename it: mv $CODEX_LNK ${CODEX_LNK}.bak && ln -s $CODEX_WIN $CODEX_LNK"
    mv "$CODEX_LNK" "${CODEX_LNK}.bak" && ln -s "$CODEX_WIN" "$CODEX_LNK"
    echo "  Done: backed up and created symlink"
else
    ln -s "$CODEX_WIN" "$CODEX_LNK"
    echo "  Created: $CODEX_LNK → $CODEX_WIN"
fi

echo ""
echo "=== [3/6] Install nvm + Node.js LTS ==="
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "  nvm already installed"
else
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
# Load nvm
export NVM_DIR="$HOME/.nvm"
# shellcheck source=/dev/null
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

if command -v node >/dev/null 2>&1; then
    echo "  Node already installed: $(node --version)"
else
    echo "  Installing Node.js LTS..."
    nvm install --lts
    nvm use --lts
    nvm alias default node
fi

echo ""
echo "=== [4/6] Install codex CLI ==="
if command -v codex >/dev/null 2>&1; then
    echo "  codex already installed: $(codex --version 2>&1 | head -1)"
else
    echo "  Installing @openai/codex..."
    npm install -g @openai/codex
fi

echo ""
echo "=== [5/6] Install RTK ==="
if command -v rtk >/dev/null 2>&1; then
    echo "  RTK already installed: $(rtk --version 2>&1 | head -1)"
else
    echo "  Installing RTK..."
    # Try official install script
    if curl -sSfL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | bash; then
        echo "  RTK installed via install.sh"
    else
        # Fallback: winget-style binary download (for WSL)
        echo "  Trying cargo install..."
        if command -v cargo >/dev/null 2>&1; then
            cargo install --git https://github.com/rtk-ai/rtk 2>&1 | tail -3
        else
            echo "  WARN: Cannot install RTK automatically. Install manually:"
            echo "    cargo install --git https://github.com/rtk-ai/rtk"
            echo "    OR download binary from https://github.com/rtk-ai/rtk/releases"
        fi
    fi
fi

echo ""
echo "=== [6/6] Verify ==="
echo -n "  node: "; node --version 2>/dev/null || echo "MISSING"
echo -n "  npm: "; npm --version 2>/dev/null || echo "MISSING"
echo -n "  codex: "; codex --version 2>/dev/null | head -1 || echo "MISSING"
echo -n "  rtk: "; rtk --version 2>/dev/null | head -1 || echo "MISSING"
echo -n "  ~/.codex symlink: "; ls -la "$HOME/.codex" 2>/dev/null | head -1 || echo "MISSING"

echo ""
echo "=== Setup complete! ==="
echo "Next: launch codex via WSL using:"
echo "  wsl -d Ubuntu -- bash /mnt/c/Users/MrThien/.codex/scripts/launch-codex-rtk.sh"
