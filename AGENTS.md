# AGENTS.md — For AI coding assistants

This repo installs a two-layer token-efficiency stack for Hermes Agent:
RTK (compresses tool output) + Caveman (compresses agent output).
Combined savings: 65-80% fewer tokens in typical dev sessions.

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
~/.local/bin/rtk --version                             # should show v0.42.3
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
| plugins/caveman/plugin.yaml | ~/.hermes/plugins/caveman/plugin.yaml | Plugin manifest |
| plugins/caveman/__init__.py | ~/.hermes/plugins/caveman/__init__.py | llm_request middleware |
| bin/caveman | ~/.local/bin/caveman | Toggle CLI (caveman on/off/status) |
| skills/productivity/caveman/SKILL.md | ~/.hermes/skills/productivity/caveman/SKILL.md | Caveman reference |
| skills/productivity/rtk/SKILL.md | ~/.hermes/skills/productivity/rtk/SKILL.md | RTK reference |
| (downloaded) | ~/.local/bin/rtk | RTK binary (v0.42.3 Linux x86_64) |
| (rtk init) | ~/.hermes/plugins/rtk-rewrite/ | RTK auto-rewrite plugin |

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

## Privacy note

This repo contains no personal information. All commits use GitHub no-reply emails.
Installation paths are under ~/.hermes/ and ~/.local/bin/.
