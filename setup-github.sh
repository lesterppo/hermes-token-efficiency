#!/bin/bash
# Secure GitHub setup — prompts for username and token with hidden input
# Usage: bash setup-github.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

clear
echo ""
echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}  ║     Hermes Token Efficiency — GitHub Setup  ║${NC}"
echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  This will create a GitHub repo and push the"
echo -e "  RTK + Caveman token-efficiency stack."
echo ""
echo -e "  ${YELLOW}Token needs: repo, workflow scope${NC}"
echo -e "  ${YELLOW}Create at: https://github.com/settings/tokens${NC}"
echo ""

# ── GitHub username ────────────────────────────────────────────────

echo -ne "  ${BOLD}GitHub username:${NC} "
read -r GH_USER

if [ -z "$GH_USER" ]; then
    echo -e "\n  ${YELLOW}No username entered. Aborting.${NC}"
    exit 1
fi

# ── GitHub token (hidden input) ────────────────────────────────────

echo -ne "  ${BOLD}GitHub token (input hidden):${NC} "
read -rs GH_TOKEN
echo ""

if [ -z "$GH_TOKEN" ]; then
    echo -e "\n  ${YELLOW}No token entered. Aborting.${NC}"
    exit 1
fi

# ── Repo name ──────────────────────────────────────────────────────

echo ""
echo -ne "  ${BOLD}Repo name${NC} [hermes-token-efficiency]: "
read -r REPO_NAME
REPO_NAME="${REPO_NAME:-hermes-token-efficiency}"

# ── Description ────────────────────────────────────────────────────

echo -ne "  ${BOLD}Description${NC} [RTK + Caveman token-efficiency stack for Hermes Agent]: "
read -r REPO_DESC
REPO_DESC="${REPO_DESC:-RTK + Caveman token-efficiency stack for Hermes Agent — cut LLM token consumption by 65-80%}"

echo ""
echo -e "  ${CYAN}───────────────────────────────────────────────${NC}"
echo -e "  Username:  ${BOLD}${GH_USER}${NC}"
echo -e "  Repo:      ${BOLD}${GH_USER}/${REPO_NAME}${NC}"
echo -e "  Token:     ${GREEN}******** (hidden)${NC}"
echo -e "  ${CYAN}───────────────────────────────────────────────${NC}"
echo ""

echo -ne "  ${BOLD}Proceed? [Y/n]:${NC} "
read -r CONFIRM
CONFIRM="${CONFIRM:-y}"

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ] && [ "$CONFIRM" != "yes" ]; then
    echo -e "\n  Aborted."
    exit 0
fi

echo ""
echo -e "  ${CYAN}Creating repo and pushing...${NC}"
echo ""

# ── Create repo via GitHub API ─────────────────────────────────────

REPO_DIR="/home/peter/hermes-token-efficiency"
cd "$REPO_DIR"

# Init git if not already
if [ ! -d .git ]; then
    git init
    git config user.name "$GH_USER"
    git config user.email "${GH_USER}@users.noreply.github.com"
fi

# Create repo on GitHub
CREATE_RESPONSE=$(curl -s -X POST "https://api.github.com/user/repos" \
    -H "Authorization: token ${GH_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    -d "$(python3 -c "
import json
print(json.dumps({
    'name': '$REPO_NAME',
    'description': '$REPO_DESC',
    'private': False,
    'has_issues': True,
    'has_projects': False,
    'has_wiki': False,
    'auto_init': False
}))
")" 2>&1)

# Check for errors
if echo "$CREATE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'html_url' in d else 1)" 2>/dev/null; then
    CLONE_URL=$(echo "$CREATE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['ssh_url'])")
    HTML_URL=$(echo "$CREATE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['html_url'])")
    echo -e "  ${GREEN}Repo created: ${HTML_URL}${NC}"
else
    ERROR_MSG=$(echo "$CREATE_RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for err in d.get('errors', []):
    print(err.get('message', ''))
print(d.get('message', ''))
" 2>/dev/null)
    echo -e "  ${YELLOW}Repo may already exist or error: ${ERROR_MSG}${NC}"
    CLONE_URL="git@github.com:${GH_USER}/${REPO_NAME}.git"
    HTML_URL="https://github.com/${GH_USER}/${REPO_NAME}"
fi

# ── Set up remote with token ───────────────────────────────────────

REMOTE_URL="https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"

# Remove existing origin if present
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

# ── Stage and commit ───────────────────────────────────────────────

git add -A
git commit -m "Initial commit: RTK + Caveman token-efficiency stack for Hermes Agent

- RTK plugin: pre_tool_call hook compresses terminal output 60-90%
- Caveman plugin: llm_request middleware compresses agent output ~66-75%
- Skills: RTK and Caveman reference documentation
- CLI: caveman on/off toggle script
- install.sh: one-command setup

Combined token savings: 65-80% in typical dev sessions.
Credits: rtk-ai/rtk (Apache 2.0), JuliusBrussee/caveman (MIT)" 2>/dev/null || echo "Nothing to commit"

# ── Push ───────────────────────────────────────────────────────────

echo ""
echo -e "  ${CYAN}Pushing to GitHub...${NC}"

if git push -u origin main 2>&1; then
    echo ""
    echo -e "  ${GREEN}${BOLD}✓ Done!${NC}"
    echo ""
    echo -e "  Repo: ${CYAN}${HTML_URL}${NC}"
    echo ""
    echo -e "  For another Hermes agent to install:"
    echo -e "  ${BOLD}  git clone ${HTML_URL}.git${NC}"
    echo -e "  ${BOLD}  cd ${REPO_NAME} && bash install.sh${NC}"
    echo ""
else
    # Try master if main fails
    echo -e "  ${YELLOW}Push to main failed, trying master...${NC}"
    git branch -M master
    git push -u origin master 2>&1
    echo ""
    echo -e "  ${GREEN}${BOLD}✓ Done!${NC}"
    echo ""
    echo -e "  Repo: ${CYAN}${HTML_URL}${NC}"
fi

# Clean token from git config (keep remote but remove credentials)
git remote set-url origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
