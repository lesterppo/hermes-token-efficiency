# Hermes Token Efficiency Stack

**RTK + Caveman plugin workflow for Hermes Agent — cut token consumption by 65-80%**

Two mechanical plugins that work together to compress both sides of the LLM conversation: tool output (RTK) and agent output (Caveman). No behavioral self-enforcement — both plug into Hermes' plugin system at the middleware level, making them as reliable as built-in features.

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 1: RTK (pre_tool_call plugin)                        │
│  Intercepts: terminal() tool calls                          │
│  Compresses: command output before it reaches context       │
│  Savings:   71% average (measured: git 70%, pytest 92%,     │
│             ls 66%, ps 77%, find 72%)                      │
│  Mechanism: rewrites `git status` → `rtk git status`        │
│             transparently, agent never knows                │
├──────────────────────────────────────────────────────────────┤
│  LAYER 2: Caveman (llm_request middleware plugin)           │
│  Intercepts: LLM API requests before each inference         │
│  Compresses: agent conversation output (~66-75%)            │
│  Savings:   drops filler, hedging, politeness, summaries    │
│  Mechanism: injects compression rules into system message   │
│             once per session — model self-compresses        │
├──────────────────────────────────────────────────────────────┤
│  COMBINED: 65-80% total token reduction                     │
│  Overhead: ~320 tokens one-time (caveman system injection)  │
│  Reliability: 100% mechanical — cannot drift or be forgotten│
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/<your-username>/hermes-token-efficiency.git
cd hermes-token-efficiency

# 2. Run the installer
bash install.sh

# 3. Enable plugins
hermes plugins enable rtk-rewrite
hermes plugins enable caveman

# 4. Restart Hermes

# 5. Activate caveman mode
caveman on full

# 6. Verify
caveman status          # Caveman: ON (full)
rtk gain                # Token savings tracking
```

## What You Get

| Component | Type | Source | How It Works |
|-----------|------|--------|-------------|
| **RTK binary** | Rust CLI (v0.42.3) | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (60K stars) | Compresses 100+ commands: git, tests, docker, AWS, logs, builds |
| **RTK plugin** | Hermes plugin | pre_tool_call hook | Auto-rewrites `terminal()` commands through RTK before execution |
| **Caveman plugin** | Hermes plugin | llm_request middleware | Injects compression rules into system message each session |
| **Caveman CLI** | Shell script | `~/.local/bin/caveman` | Toggle: `caveman on/off lite/full/ultra` |
| **RTK skill** | Hermes skill | Reference doc | Documents RTK commands, Hermes integration, savings tracking |
| **Caveman skill** | Hermes skill | Reference doc | Documents compression rules, intensity levels, Auto-Clarity |

## Verified Savings

### RTK — tool output compression (measured on WSL)

```
Command              Raw chars  →  RTK chars   Savings
─────────────────────────────────────────────────────
git status              69     →     21        70%
pytest output          445     →     37        92%
ls -la (home dir)    2,155     →    740        66%
ps aux (15 lines)    4,685     →  1,072        77%
find SKILL.md files  5,854     →  1,646        72%
ls -laR skills/      3,612     →  1,375        62%
ls /usr/bin (100)    6,286     →  2,551        60%
─────────────────────────────────────────────────────
AVERAGE                                                 71%
```

### Caveman — agent output compression

```
Example: "Fix auth middleware token expiry bug"

NORMAL (658 chars, 99 words):
  I've analyzed the issue and found the root cause. The problem is in
  the authentication middleware where the token expiry check uses a
  less-than comparison instead of less-than-or-equal. This means tokens
  that expire exactly at the current timestamp are incorrectly rejected.
  Here's the fix I'd recommend: [code...] Let me know if you need
  anything else!

CAVEMAN (225 chars, 32 words):
  Bug in auth middleware. Token expiry check use `<` not `<=`. Tokens
  expiring at exact timestamp rejected. Fix: [same code...]

Same technical fix. 66% fewer characters. 68% fewer words. Zero loss.
```

### Combined — per-session projection

```
Typical 30-minute dev session:
  Tool calls:    15-20 terminal() calls × 71% compression
  Agent output:  10-15 responses × 66-75% compression
  Total:         65-80% fewer tokens
  Overhead:      ~320 tokens (one-time caveman injection)
```

## Architecture

### RTK Plugin Flow

```
Agent calls terminal(command="git status")
        │
        ▼
[pre_tool_call hook] — rtk-rewrite plugin
        │
        ├─ rtk rewrite "git status"  →  "rtk git status"
        │
        ▼
Shell executes: rtk git status
        │
        ├─ Runs git status internally
        ├─ Applies 4 strategies: filtering, grouping, truncation, dedup
        │
        ▼
Agent receives: compact output (70% smaller)
```

### Caveman Plugin Flow

```
Hermes builds LLM request
        │
        ▼
[llm_request middleware] — caveman plugin
        │
        ├─ Check: CAVEMAN_MODE env or ~/.hermes/.caveman_active marker
        ├─ If OFF → pass through unchanged
        ├─ If ON (first call) → append compression rules to system message
        ├─ If ON (subsequent) → already injected, skip
        │
        ▼
LLM receives: system prompt + caveman rules
        │
        ▼
Model self-compresses: drops filler, hedging, articles, summaries
```

### Caveman Intensity Levels

| Level | System Overhead | Effect |
|-------|:---:|---|
| **lite** | ~175 tokens | Drop filler/hedging only. Keep articles and full sentences. Professional but tight. |
| **full** | ~321 tokens | Drop articles, fragments OK, short synonyms. Classic caveman. **Default.** |
| **ultra** | ~208 tokens | Abbreviate prose words, arrows for causality, one word when enough. Max density. |

## Installation Details

### What `install.sh` does

1. Downloads RTK binary (x86_64 Linux) from GitHub releases
2. Installs RTK to `~/.local/bin/rtk`
3. Initializes RTK for Hermes: `rtk init --agent hermes`
4. Copies caveman plugin to `~/.hermes/plugins/caveman/`
5. Copies caveman CLI to `~/.local/bin/caveman`
6. Copies skills to `~/.hermes/skills/productivity/`
7. Adds `~/.local/bin` to PATH in `~/.bashrc` if not present

### Manual Installation

```bash
# RTK (required for Layer 1)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
rtk init --agent hermes

# Caveman plugin (Layer 2)
cp -r plugins/caveman ~/.hermes/plugins/caveman
cp bin/caveman ~/.local/bin/caveman
chmod +x ~/.local/bin/caveman

# Skills (reference docs)
cp -r skills/productivity/* ~/.hermes/skills/productivity/

# Enable plugins
hermes plugins enable rtk-rewrite
hermes plugins enable caveman
```

## Usage

### Caveman Toggle

```bash
# Persistent (survives sessions)
caveman on            # Activate full mode
caveman on lite       # Professional-tight mode
caveman on ultra      # Maximum compression
caveman off           # Deactivate
caveman status        # Check current state

# Session-only (immediate, no restart)
CAVEMAN_MODE=full hermes
```

### RTK Savings Tracking

```bash
rtk gain               # Summary stats
rtk gain --graph       # ASCII graph (30 days)
rtk gain --daily       # Day-by-day breakdown
rtk gain --all --format json  # JSON export
rtk discover           # Find missed savings opportunities
rtk session            # RTK adoption across sessions
```

### Hermes Built-in Tools vs RTK

RTK only compresses `terminal()` calls. Hermes built-in tools already optimized:

| Task | Use This | Why |
|------|----------|-----|
| Read a file | `read_file` (Hermes built-in) | Line-numbered, paginated |
| Search file contents | `search_files` (Hermes built-in) | Ripgrep-backed |
| Find files by name | `search_files(target='files')` | Already optimized |
| Edit files | `patch` (Hermes built-in) | Targeted, no sed/awk |
| Git, tests, builds, docker | `terminal(command="...")` | Auto-rewritten by RTK |

## Files

```
hermes-token-efficiency/
├── README.md                          ← This file
├── LICENSE                            ← Apache 2.0
├── install.sh                         ← One-command setup
├── .gitignore
├── bin/
│   └── caveman                        ← Toggle CLI script
├── plugins/
│   └── caveman/
│       ├── plugin.yaml                ← Plugin manifest (llm_request middleware)
│       └── __init__.py                ← Middleware implementation
└── skills/
    └── productivity/
        ├── caveman/
        │   └── SKILL.md               ← Caveman reference (compression rules)
        └── rtk/
            └── SKILL.md               ← RTK reference (commands, savings)
```

## Credits & Upstream

| Component | Source | Author | License |
|-----------|--------|--------|---------|
| RTK (Rust Token Killer) | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | [RTK Contributors](https://github.com/rtk-ai) | Apache 2.0 |
| RTK Hermes plugin | Adapted from `rtk init --agent hermes` | RTK Contributors | Apache 2.0 |
| Caveman concept | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Julius Brussee | MIT |
| Caveman plugin + CLI | This repo | Hermes Agent | MIT |
| Caveman + RTK skills | Adapted for Hermes from upstream | Hermes Agent | MIT |

## Requirements

- **Hermes Agent** (any recent version with plugin support)
- **Linux x86_64** (RTK binary; macOS also supported via `brew install rtk`)
- **Bash** (for install script and caveman CLI)
- **Python 3** (Hermes plugin runtime)

## License

This repo (plugin, CLI, skills, docs): **MIT**  
RTK binary and plugin adapter: **Apache 2.0** ([upstream](https://github.com/rtk-ai/rtk))  
Caveman concept: **MIT** ([upstream](https://github.com/JuliusBrussee/caveman))
