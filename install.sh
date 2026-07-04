#!/bin/bash
# install.sh — Set up RTK + Caveman token-efficiency stack for Hermes Agent
#
# Usage: bash install.sh
#
# What this does:
#   1. Downloads and installs RTK binary (x86_64 Linux)
#   2. Initializes RTK Hermes plugin (rtk init --agent hermes)
#   3. Installs Caveman plugin to ~/.hermes/plugins/caveman/
#   4. Installs Caveman CLI to ~/.local/bin/caveman
#   5. Installs RTK and Caveman skills to ~/.hermes/skills/productivity/
#   6. Ensures ~/.local/bin is in PATH
#
# After install, run:
#   hermes plugins enable rtk-rewrite
#   hermes plugins enable caveman
#   caveman on full
#   # Restart Hermes

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
LOCAL_BIN="$HOME/.local/bin"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Hermes Token Efficiency Stack — RTK + Caveman    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Pre-flight checks ──────────────────────────────────────────────

if [ ! -d "$HERMES_HOME" ]; then
    echo -e "${YELLOW}Warning: $HERMES_HOME not found. Creating...${NC}"
    mkdir -p "$HERMES_HOME"
fi

mkdir -p "$LOCAL_BIN"
mkdir -p "$HERMES_HOME/plugins"
mkdir -p "$HERMES_HOME/skills/productivity"

# ── Step 1: RTK Binary ─────────────────────────────────────────────

echo -e "${CYAN}[1/5] Installing RTK binary...${NC}"

RTK_VERSION="0.43.0"
RTK_URL="https://github.com/rtk-ai/rtk/releases/download/v${RTK_VERSION}/rtk-x86_64-unknown-linux-musl.tar.gz"

if command -v rtk &>/dev/null; then
    CURRENT=$(rtk --version 2>/dev/null | awk '{print $2}')
    echo -e "${GREEN}  RTK already installed: v${CURRENT}${NC}"
else
    echo "  Downloading RTK v${RTK_VERSION}..."
    if curl -fsSL "$RTK_URL" -o /tmp/rtk-install.tar.gz; then
        tar xzf /tmp/rtk-install.tar.gz -C /tmp/
        cp /tmp/rtk "$LOCAL_BIN/rtk"
        chmod +x "$LOCAL_BIN/rtk"
        rm -f /tmp/rtk-install.tar.gz /tmp/rtk
        echo -e "${GREEN}  RTK v${RTK_VERSION} installed to $LOCAL_BIN/rtk${NC}"
    else
        echo -e "${YELLOW}  Could not download RTK. Install manually: brew install rtk${NC}"
        echo -e "${YELLOW}  Or: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh${NC}"
    fi
fi

# ── Step 2: RTK Hermes Plugin ──────────────────────────────────────

echo -e "${CYAN}[2/5] Initializing RTK for Hermes...${NC}"

export PATH="$LOCAL_BIN:$PATH"

if [ -d "$HERMES_HOME/plugins/rtk-rewrite" ]; then
    echo -e "${GREEN}  RTK Hermes plugin already installed${NC}"
else
    if command -v rtk &>/dev/null; then
        rtk init --agent hermes 2>&1 | sed 's/^/  /'
        echo -e "${GREEN}  RTK plugin installed${NC}"
    else
        echo -e "${YELLOW}  RTK binary not found — skipping plugin init${NC}"
    fi
fi

# ── Step 3: Caveman Plugin ─────────────────────────────────────────

echo -e "${CYAN}[3/5] Installing Caveman plugin...${NC}"

if [ -d "$REPO_DIR/plugins/caveman" ]; then
    rm -rf "$HERMES_HOME/plugins/caveman"
    cp -r "$REPO_DIR/plugins/caveman" "$HERMES_HOME/plugins/caveman"
    echo -e "${GREEN}  Caveman plugin installed to $HERMES_HOME/plugins/caveman/${NC}"
else
    echo -e "${RED}  Error: plugins/caveman/ not found in repo directory${NC}"
    exit 1
fi

# ── Step 4: Caveman CLI ────────────────────────────────────────────

echo -e "${CYAN}[4/5] Installing Caveman CLI...${NC}"

if [ -f "$REPO_DIR/bin/caveman" ]; then
    cp "$REPO_DIR/bin/caveman" "$LOCAL_BIN/caveman"
    chmod +x "$LOCAL_BIN/caveman"
    echo -e "${GREEN}  Caveman CLI installed to $LOCAL_BIN/caveman${NC}"
else
    echo -e "${RED}  Error: bin/caveman not found in repo directory${NC}"
    exit 1
fi

# ── Step 5: Skills ─────────────────────────────────────────────────

echo -e "${CYAN}[5/5] Installing skills...${NC}"

for skill in caveman rtk; do
    if [ -d "$REPO_DIR/skills/productivity/$skill" ]; then
        rm -rf "$HERMES_HOME/skills/productivity/$skill"
        cp -r "$REPO_DIR/skills/productivity/$skill" "$HERMES_HOME/skills/productivity/$skill"
        echo -e "${GREEN}  $skill skill installed${NC}"
    else
        echo -e "${YELLOW}  skills/productivity/$skill/ not found — skipping${NC}"
    fi
done

# ── PATH setup ─────────────────────────────────────────────────────

if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "$LOCAL_BIN" "$HOME/.bashrc"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
    fi
    export PATH="$LOCAL_BIN:$PATH"
fi

# ── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Installation complete!                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Next steps:"
echo ""
echo -e "  ${CYAN}1. Enable plugins:${NC}"
echo "     hermes plugins enable rtk-rewrite"
echo "     hermes plugins enable caveman"
echo ""
echo -e "  ${CYAN}2. Restart Hermes${NC}"
echo ""
echo -e "  ${CYAN}3. Activate caveman:${NC}"
echo "     caveman on full"
echo ""
echo -e "  ${CYAN}4. Verify:${NC}"
echo "     caveman status     # Caveman: ON (full)"
echo "     rtk gain           # Token savings (after some commands)"
echo ""
echo -e "  ${CYAN}5. Check skills:${NC}"
echo "     # In Hermes: skill_view(name='caveman')"
echo "     # In Hermes: skill_view(name='rtk')"
echo ""
