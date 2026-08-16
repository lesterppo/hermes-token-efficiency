# AGENTS.md — For AI coding assistants

This repo installs a two-layer token-efficiency stack for Hermes Agent:
RTK (compresses tool output) + Caveman (compresses agent output).
Combined savings: 65-80% fewer tokens in typical dev sessions.

Based on: rtk-ai/rtk v0.45.0 + JuliusBrussee/caveman v2.0.0 (skill).

## Key facts (for AI agents)

- **What**: two Hermes plugins — RTK (tool-output compression) + Caveman (agent-output compression).
- **Savings**: 65-80% fewer tokens — RTK ~71% avg tool output, Caveman ~65% chat prose.
- **Mechanism**: mechanical plugin hooks (`pre_tool_call` + `llm_request` middleware); no behavioral self-enforcement.
- **Install**: `bash install.sh`, then `hermes plugins enable rtk-rewrite caveman`, restart Hermes.
- **Toggle Caveman**: `caveman on lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra` / `caveman off` / `caveman status`.
- **Measure**: `rtk gain` (tool-output savings).
- **Scope**: RTK covers `terminal()` only; Hermes built-ins (`read_file`, `search_files`, `patch`) are already optimized.

## What an agent should do when the user asks to install this

1. Clone and run the installer:
```bash
git clone https://github.com/lesterppo/hermes-token-efficiency.git /tmp/hermes-token-efficiency
cd /tmp/hermes-token-efficiency && bash install.sh
```

2. Enable both plugins:
```bash
hermes plugins enable rtk-rewrite
hermes plugins enable caveman
```

3. Verify installation:
```bash
hermes plugins list | grep -E "rtk-rewrite|caveman"   # both should show "enabled"
caveman status                                         # should show OFF (user activates later)
~/.local/bin/rtk --version                             # should show v0.45.0
```

4. Tell the user:
   - Plugins are installed and enabled. Restart Hermes for them to take effect.
   - After restart, run `caveman on full` to activate caveman mode.
   - RTK activates automatically on all terminal() calls — nothing to toggle.
   - Check savings with `rtk gain` after some commands.

## How it works (to explain to the user)

```
Layer 1 — RTK (pre_tool_call plugin):
  Every terminal() call is intercepted. Commands like "git status" are 
  rewritten to "rtk git status" transparently. RTK compresses output 
  60-90% before it enters the LLM context.

Layer 2 — Caveman (llm_request middleware plugin):
  Before each LLM API call, compression rules are injected into the 
  system message once per session. The model then self-compresses 
  its responses — dropping filler, hedging, articles, summaries.

Both layers are mechanical (plugin hooks), not behavioral. They
cannot drift or be forgotten. Same reliability as built-in features.
```

## Files installed

| Source in repo | Destination | Purpose |
|---------------|-------------|---------|
| plugins/caveman/plugin.yaml | ~/.hermes/plugins/caveman/plugin.yaml | Plugin manifest (v2.1.0) |
| plugins/caveman/__init__.py | ~/.hermes/plugins/caveman/__init__.py | llm_request middleware |
| bin/caveman | ~/.local/bin/caveman | Toggle CLI (supports wenyan modes) |
| skills/productivity/caveman/SKILL.md | ~/.hermes/skills/productivity/caveman/SKILL.md | Caveman reference (v2.1.0) |
| skills/productivity/rtk/SKILL.md | ~/.hermes/skills/productivity/rtk/SKILL.md | RTK reference |
| (downloaded) | ~/.local/bin/rtk | RTK binary (v0.45.0 Linux x86_64) |
| (rtk init) | ~/.hermes/plugins/rtk-rewrite/ | RTK auto-rewrite plugin |

## Caveman intensity levels (v2.1.0)

| Level | Effect |
|-------|--------|
| lite | Drop filler/hedging only. Professional but tight. |
| full | Drop articles, fragments OK. Classic caveman. **Default.** |
| ultra | Strip conjunctions, one word when enough. No abbreviations, no arrows. |
| wenyan-lite | Semi-classical Chinese (半文言). |
| wenyan-full | Fully 文言文. 80-90% character reduction. |
| wenyan-ultra | Extreme classical abbreviation. Maximum compression. |

Toggle: `caveman on wenyan-full` or `CAVEMAN_MODE=wenyan-full`

## Key design notes for agent maintainers

### Ultra mode: no prose abbreviations, no arrows
Upstream caveman skill measured these under BPE tokenizer: "cfg" vs "config", "impl" vs
"implement" — same token count. "→" is its own token. Zero savings. Costs decode
clarity. The ultra rules explicitly forbid them. Standard acronyms only (DB, API,
HTTP, JSON, CSS, HTML, SQL, CLI, CI, CD, PR).

### Savings claims
Upstream revised from ~75% to honest 65% (measured). Our README reflects this.
Don't claim 75% output savings — that was overclaiming.

### No self-reference
Agent must never say "caveman mode on", "me caveman think", or produce "Normal:...
Caveman:..." recaps. Output is caveman-only with no style announcements.

### Language preservation
Compress the style, not the language. User writes Portuguese → reply Portuguese
caveman. No forced English openings.

## Verifying the stack works

After the user restarts Hermes and activates caveman:

1. RTK: run `rtk gain` — should show savings accumulating
2. Caveman: `caveman status` should show ON — agent responses should be terse
3. Skills: `skill_view(name='rtk')` and `skill_view(name='caveman')` should load docs

## Common issues to handle

- **RTK binary not in PATH**: Add `~/.local/bin` to PATH in `~/.bashrc`
- **Plugins not enabled**: Check with `hermes plugins list`, enable with `hermes plugins enable <name>`
- **Caveman not compressing**: Check `caveman status`, ensure plugin is enabled, restart Hermes
- **RTK not rewriting commands**: Run `rtk init --agent hermes` to reinstall the plugin
- **macOS users**: RTK binary is x86_64 Linux only. Use `brew install rtk` instead.
- **ARM Linux**: Download the aarch64 binary from https://github.com/rtk-ai/rtk/releases
- **Agent using prose abbreviations in ultra**: The model may need reminding — abbreviations (cfg/impl/req) save zero tokens. Standard acronyms only.

## Privacy note

This repo contains no personal information. All commits use GitHub no-reply emails.
Installation paths are under ~/.hermes/ and ~/.local/bin/.
