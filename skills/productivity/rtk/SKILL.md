---
name: rtk
description: Use when working with terminal commands in dev workflows — git, tests, builds, linting, package managers, docker, AWS, logs. RTK is a CLI proxy that auto-compresses command output 60-90% before it reaches your context. Already installed and auto-rewriting via Hermes plugin. Check savings with "rtk gain".
version: 1.0.0
author: Hermes Agent (adapted from rtk-ai/rtk v0.42.3)
license: Apache-2.0
metadata:
  hermes:
    tags: [productivity, tokens, devops, terminal, compression, rtk, efficiency]
    related_skills: [caveman, find-skills]
---

# RTK — Rust Token Killer

RTK is a high-performance CLI proxy that filters and compresses command output before it reaches your context. Single Rust binary, <10ms overhead, 100+ supported commands, 60-90% token reduction on common dev operations.

**Status**: Installed (v0.42.3 at `~/.local/bin/rtk`). Hermes plugin active — terminal commands auto-rewritten through RTK via `pre_tool_call` hook.

## When to Use

- Running terminal commands for dev workflows (git, tests, builds, linting)
- Checking token savings: `rtk gain`
- Finding missed optimization opportunities: `rtk discover`
- Manually wrapping a noisy command: `rtk <command>`
- Don't use for: Hermes built-in tools (`read_file`, `search_files`, `patch`) — those don't go through terminal and RTK can't intercept them. Use the built-in tools when they're more efficient than shell equivalents.

## How It Works (Hermes Integration)

The Hermes plugin at `~/.hermes/plugins/rtk-rewrite/` hooks into every `terminal()` call:

```
Agent calls: terminal(command="git status")
Plugin intercepts → rewrites to: terminal(command="rtk git status")
RTK runs git status → compresses output → agent sees compact result
```

This is transparent — you don't need to prefix commands with `rtk`. Just use normal terminal commands and the plugin handles it.

**Exception**: Hermes built-in tools (`read_file`, `search_files`, `patch`) bypass the terminal entirely. RTK cannot intercept them. This is correct — Hermes' built-in tools are already optimized and don't benefit from RTK wrapping.

## Token Savings Reference

Real-world savings from 30-minute dev sessions:

| Operation | Standard Tokens | RTK Tokens | Savings |
|-----------|:---:|:---:|:---:|
| `ls` / `tree` | 2,000 | 400 | 80% |
| `cat` / `read` (shell) | 40,000 | 12,000 | 70% |
| `grep` / `rg` (shell) | 16,000 | 3,200 | 80% |
| `git status` | 3,000 | 600 | 80% |
| `git diff` | 10,000 | 2,500 | 75% |
| `git log` | 2,500 | 500 | 80% |
| `git add/commit/push` | 1,600 | 120 | 92% |
| `cargo test` / `npm test` | 25,000 | 2,500 | 90% |
| `ruff check` | 3,000 | 600 | 80% |
| `pytest` | 8,000 | 800 | 90% |
| `docker ps` | 900 | 180 | 80% |
| **Session total** | **~118,000** | **~23,900** | **80%** |

## Key Commands

### Git (highest savings)
```bash
git status                      # auto-rewritten → compact status
git diff                        # auto-rewritten → condensed diff
git log -n 10                   # auto-rewritten → one-line commits
git add / commit / push / pull  # auto-rewritten → "ok" / "ok abc1234" / "ok main"
```

### Test Runners (90% savings — failures only)
```bash
pytest                          # auto-rewritten → failures only
cargo test                      # auto-rewritten → failures only
go test                         # auto-rewritten → NDJSON, -90%
npm test / jest / vitest        # auto-rewritten → failures only
playwright test                 # auto-rewritten → failures only
```

### Build & Lint
```bash
cargo build / cargo clippy      # auto-rewritten → -80%
ruff check                      # auto-rewritten → JSON, -80%
tsc                             # auto-rewritten → errors grouped by file
next build                      # auto-rewritten → compact
```

### Containers
```bash
docker ps                       # auto-rewritten → compact list
docker logs <container>         # auto-rewritten → deduplicated
kubectl pods / logs / services  # auto-rewritten → compact
```

### Package Managers
```bash
pnpm list                       # auto-rewritten → compact tree
pip list / pip outdated         # auto-rewritten → compact
bundle install                  # auto-rewritten → strip "Using" lines
```

### AWS
```bash
aws sts get-caller-identity     # auto-rewritten → one-line
aws ec2 describe-instances      # auto-rewritten → compact list
aws lambda list-functions       # auto-rewritten → name/runtime/memory
aws logs get-log-events         # auto-rewritten → timestamped messages
aws s3 ls                       # auto-rewritten → truncated
```

### Manual RTK Commands (when you want explicit control)
```bash
rtk read file.rs                # Smart file reading (vs Hermes built-in read_file)
rtk read file.rs -l aggressive  # Signatures only, strips bodies
rtk smart file.rs               # 2-line heuristic code summary
rtk find "*.rs" .               # Compact find results
rtk grep "pattern" .            # Grouped search results
rtk diff file1 file2            # Condensed diff
rtk json config.json            # Structure without values
rtk deps                        # Dependencies summary
rtk env -f AWS                  # Filtered env vars
rtk log app.log                 # Deduplicated logs
rtk summary <command>           # Heuristic summary of any command
rtk err <command>               # Filter errors only from any command
```

### Token Savings Analytics
```bash
rtk gain                        # Summary stats
rtk gain --graph                # ASCII graph (last 30 days)
rtk gain --history              # Recent command history
rtk gain --daily                # Day-by-day breakdown
rtk gain --all --format json    # JSON export for dashboards

rtk discover                    # Find missed savings opportunities
rtk discover --all --since 7    # All projects, last 7 days

rtk session                     # Show RTK adoption across recent sessions
```

## Global Flags

```bash
-u, --ultra-compact    # ASCII icons, inline format (extra savings)
-v, --verbose          # Increase verbosity (-v, -vv, -vvv)
```

## When to Use Shell Commands vs Hermes Built-In Tools

Hermes has optimized built-in tools that don't go through the terminal. Choose:

| Task | Use This | Why |
|------|----------|-----|
| Read a file | `read_file` (Hermes built-in) | Line-numbered, paginated, already efficient |
| Search file contents | `search_files` (Hermes built-in) | Ripgrep-backed, faster than `grep` |
| Find files by name | `search_files(target='files')` | Already optimized |
| Edit files | `patch` (Hermes built-in) | Targeted find/replace, no sed/awk |
| Git operations | `terminal(command="git ...")` | Auto-rewritten by RTK plugin |
| Run tests | `terminal(command="pytest ...")` | Auto-rewritten by RTK plugin |
| Build/lint | `terminal(command="cargo build")` | Auto-rewritten by RTK plugin |
| Docker/k8s | `terminal(command="docker ...")` | Auto-rewritten by RTK plugin |
| List directory | `terminal(command="ls ...")` | Auto-rewritten by RTK plugin |

**Rule of thumb**: Use Hermes built-in tools for file operations. Use `terminal()` for everything else — RTK handles the compression.

See also: `references/benchmarks.md` for measured compression data (80% on ls, 64% on find, 65% on pip list) and installation notes.

## RTK Config

Config at `~/.config/rtk/config.toml`:
- Tracking enabled, 90-day history
- Tee mode: saves full output for failures (recovery if compression hides something)
- Auto-ignores: `.git`, `node_modules`, `target`, `__pycache__`, `.venv`, `vendor`

To customize:
```bash
rtk config   # Show current config
# Edit ~/.config/rtk/config.toml directly
```

## When RTK Might Hide Something Important

RTK compresses aggressively. If you suspect compressed output is hiding critical info:

1. **Check tee recovery**: RTK saves full output for failed commands at `~/.rtk/tee/`
2. **Run without RTK**: `rtk proxy <command>` — passes through raw output (still tracked)
3. **Increase verbosity**: `rtk <command> -vvv` — shows what RTK filtered
4. **Disable temporarily**: The plugin fails open — if `rtk` binary is missing, commands pass through unchanged

## Common Pitfalls

1. **Using `cat`/`grep`/`find` in terminal instead of Hermes built-ins.** `read_file`, `search_files`, and `search_files(target='files')` are faster and don't consume terminal tokens. Use them when you just need to read/search.
2. **Forgetting RTK is active.** The auto-rewrite is transparent. If you're confused why output looks different, RTK is compressing it. Check with `rtk gain` to see the savings.
3. **RTK binary not in PATH after WSL restart.** The binary is at `~/.local/bin/rtk`. If the plugin warns "rtk binary not found", ensure `~/.local/bin` is in PATH: `export PATH="$HOME/.local/bin:$PATH"` (add to `~/.bashrc`).
4. **Running `rtk gain` before any commands.** Shows "No tracking data yet." Run some commands first, then check savings.
5. **Using `rtk read` instead of Hermes `read_file`.** Hermes' built-in `read_file` gives line numbers, pagination, and doesn't consume terminal tokens. Only use `rtk read` when you specifically need aggressive mode (`-l aggressive`) or a smart summary (`rtk smart`).

## Verification Checklist

- [ ] `rtk --version` returns v0.42.3+
- [ ] Plugin at `~/.hermes/plugins/rtk-rewrite/__init__.py` exists
- [ ] Run `git status` → output is compact (auto-rewritten)
- [ ] Run `rtk gain` → shows tracking data (after some commands)
- [ ] `~/.local/bin` is in PATH (in `~/.bashrc`)
- [ ] Hermes built-in tools (`read_file`, `search_files`, `patch`) still used for file operations
