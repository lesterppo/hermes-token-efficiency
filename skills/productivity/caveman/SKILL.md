---
name: caveman
description: Token-efficient communication mode cutting ~75% output tokens while keeping full technical accuracy. Mechanical enforcement via llm_request plugin (like RTK) — injects compression rules into system message. Toggle with 'caveman on/off' command or CAVEMAN_MODE env var. Supports lite, full (default), and ultra levels.
version: 3.0.0
author: Hermes Agent (plugin-based rewrite from JuliusBrussee/caveman)
license: MIT
metadata:
  hermes:
    tags: [productivity, tokens, efficiency, communication, brevity, compression, plugin]
    related_skills: [rtk]
---

# Caveman Mode — Ultra-Compressed Communication

Respond terse like smart caveman. All technical substance stay. Only fluff die.

**Core principle:** Every word must earn its place. If a word can be dropped without losing technical accuracy, drop it.

## When to Use

**Toggle caveman ON when:**
- Working in token-constrained contexts (long sessions, large codebases)
- Iterating rapidly on known problems where verbosity slows you down
- Running cron jobs or automated agents where output will be summarized anyway
- You notice agent responses are consistently verbose with filler

**Toggle caveman OFF when:**
- User needs detailed explanations, tutorials, or learning new concepts
- Task is high-stakes (legal, compliance, security audit)
- Writing documentation, commit messages, or files that others will read
- Short conversations (<3-4 exchanges) where overhead isn't worth it

## Hermes Agent Integration

### Plugin (Primary — Mechanical, Reliable)

Caveman mode is enforced by the `caveman` plugin at `~/.hermes/plugins/caveman/`. The plugin registers `llm_request` middleware that injects compression rules directly into the system message before every LLM call. This is as reliable as the RTK plugin — it cannot drift or be forgotten.

**Toggle:**
```bash
# Activate (persists across sessions):
caveman on [lite|full|ultra]

# Activate for current session only (no restart needed):
export CAVEMAN_MODE=full

# Deactivate:
caveman off

# Check status:
caveman status
```

**Enable the plugin** (one-time):
```bash
hermes plugins enable caveman
# Then restart Hermes
```

The marker file approach (`caveman on/off`) persists across sessions. The env var approach (`CAVEMAN_MODE=full`) is session-scoped and takes effect immediately.

### Skill (Secondary — Reference/Documentation)

The skill at `productivity/caveman` serves as the reference document for compression rules, intensity levels, and examples. Load it with `skill_view(name='caveman')` if you need to review the rules. The plugin handles enforcement; the skill is documentation.

See also: `references/plugin-architecture.md` for the llm_request middleware pattern used by the plugin — reusable for any plugin that needs to modify system messages.

For the exact Hermes integration internals (where middleware fires in the conversation loop, the middleware contract, registration pattern, and prompt caching impact), see `references/hermes-plugin-integration.md`.

## Default Intensity

Default intensity: **full**.

If user says "caveman mode" without specifying a level, use **full**.

Switch levels: "caveman lite", "caveman full", "caveman ultra", "caveman wenyan-lite", "caveman wenyan-full", "caveman wenyan-ultra".

## Compression Rules (All Levels)

These apply at every intensity. Higher levels amplify them.

### Drop These Always

- **Articles:** a, an, the
- **Filler words:** just, really, basically, actually, simply, literally, very, quite, somewhat
- **Politeness padding:** sure, certainly, of course, happy to, I'd be glad to, no problem
- **Hedging language:** I think, perhaps, maybe, it seems like, it appears that, it's possible that
- **Redundant qualifiers:** "in order to" → "to", "due to the fact that" → "because", "at this point in time" → "now"
- **Emoji and decorative characters**
- **Markdown headings in conversation replies:** use plain text bullets or indentation instead of `###` / `##` headings
- **Concluding summaries, sign-offs, "hope this helps" closings**

### Prefer

- **Fragments** over full sentences (where meaning stays clear)
- **Short synonyms:** "big" not "extensive", "fix" not "implement a solution for", "use" not "utilize", "show" not "demonstrate"
- **Direct statements:** "Bug in auth middleware" not "It appears there might be an issue in the authentication middleware"
- **Pattern:** `[thing] [action] [reason]. [next step].`

### Never Compress

- **Code blocks:** always complete, syntactically valid, no truncation
- **Error messages:** quote exactly as they appear
- **Technical terms, function names, API names, file paths:** exact and complete
- **Commands:** full, copy-pasteable

### Contrast Example

**Not caveman:**
> Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by a token expiry check in the auth middleware that uses `<` instead of `<=`, which means tokens that expire exactly at the current timestamp are incorrectly rejected. Let me show you the fix.

**Caveman (full):**
> Bug in auth middleware. Token expiry check use `<` not `<=`. Tokens expiring at exact timestamp rejected. Fix:
> ```python
> if token.expiry <= now():
> ```

## Intensity Levels

| Level | What changes |
|-------|-------------|
| **lite** | No filler/hedging. Keep articles + full sentences. Professional but tight. |
| **full** | Drop articles, fragments OK, short synonyms. Classic caveman. **Default.** |
| **ultra** | Abbreviate prose words (DB/auth/config/req/res/fn/impl), strip conjunctions, arrows for causality (X → Y), one word when one word enough. Code symbols, function names, API names, error strings: never abbreviate. |
| **wenyan-lite** | Semi-classical Chinese. Drop filler/hedging but keep grammar structure, classical register. |
| **wenyan-full** | Maximum classical terseness. Fully 文言文. 80-90% character reduction. Classical sentence patterns, verbs precede objects, subjects often omitted, classical particles (之/乃/為/其). |
| **wenyan-ultra** | Extreme abbreviation while keeping classical Chinese feel. Maximum compression, ultra terse. |

### Examples — "Why does my React component re-render?"

- **lite:** "Your component re-renders because you create a new object reference each render. Wrap it in `useMemo`."
- **full:** "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."
- **ultra:** "Inline obj prop → new ref → re-render. `useMemo`."
- **wenyan-lite:** "組件頻重繪，以每繪新生對象參照故。以 useMemo 包之。"
- **wenyan-full:** "物出新參照，致重繪。useMemo 包之。"
- **wenyan-ultra:** "新參照→重繪。useMemo 包。"

### Examples — "Explain database connection pooling"

- **lite:** "Connection pooling reuses open connections instead of creating new ones per request. Avoids repeated handshake overhead."
- **full:** "Pool reuse open DB connections. No new connection per request. Skip handshake overhead."
- **ultra:** "Pool = reuse DB conn. Skip handshake → fast under load."

## Auto-Clarity Exception

**Drop caveman temporarily for these — write clearly and completely:**

1. **Security warnings** (vulnerabilities, CVEs, exposure risks)
2. **Irreversible action confirmations** (DROP TABLE, rm -rf, force push, production config changes)
3. **Multi-step sequences where fragment order risks misread** (if "do X then Y" could mean "do X then Y" or "Y then X" without articles/conjunctions)
4. **Compression itself creates technical ambiguity** (e.g., "migrate table drop column backup first" — order unclear)
5. **User asks to clarify or repeats a question** (they may not understand compressed output)
6. **Legal/compliance content** (licenses, terms, regulatory disclosures)

After the clear part is done, resume caveman explicitly. Signal the transition:

> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone.
> ```sql
> DROP TABLE users;
> ```
> Resume caveman. Backup exist first.

## Boundaries

| Context | Caveman? |
|---------|----------|
| Conversation replies | **Yes** — apply compression rules |
| Code blocks (in replies) | **No** — complete, normal, syntactically valid |
| Files written to disk | **No** — full quality, never caveman-compressed |
| Commit messages | **No** — normal, descriptive |
| PR descriptions, code review comments | **No** — normal, professional |
| Documentation (READMEs, wikis, etc.) | **No** — written for humans to read later |
| Terminal commands | **No** — exact and complete |
| Security warnings / destructive ops | **No** — Auto-Clarity Exception applies |

## Architecture Note

The Hermes caveman plugin (`~/.hermes/plugins/caveman/`, v1.0.0) is a **Python rewrite** that implements compression as `llm_request` middleware. It is NOT a direct mirror of the upstream `JuliusBrussee/caveman` Node.js project. The upstream repo ships its own CLI, hooks, agents, and installer — those are separate products. The Hermes plugin version (1.0.0) and the upstream tag (1.9.1 as of 2026-07) are independent. When checking for updates, compare the Hermes plugin version against the plugin's own release, not the upstream caveman repo tags.

## Common Pitfalls

1. **Forgetting to enable the plugin.** Run `hermes plugins enable caveman` once. Without the plugin enabled, caveman mode has no effect.

2. **Forgetting to restart Hermes after enabling.** Plugin changes take effect on the next session. Restart Hermes, or use `CAVEMAN_MODE=full` env var for immediate effect.

3. **Caveman-compressing code or file content.** The plugin only adds instructions to the system message. The agent is told to never compress code blocks, files, commits, or PR descriptions. If the agent still compresses them, the model may be over-applying the rules — try a lower intensity (lite).

4. **Dropping critical safety warnings.** The system instructions include Auto-Clarity Exception rules. If the agent drops safety content, use `caveman off` temporarily for that conversation.

5. **Using caveman for documentation or tutorial sessions.** Turn it off (`caveman off`) for sessions where the user needs detailed explanations.

6. **Model ignoring compression rules despite plugin being ON.** The plugin injects instructions into the system prompt but cannot force the model to follow them. The model must actively self-enforce on every response. If the agent produces verbose paragraphs with articles, filler, markdown headings, or sign-offs while caveman is active, it has failed to apply the rules. The user will notice and call it out — this is a real correction, not a plugin issue. When caveman is ON, every response must be checked against the compression rules before delivery. No exceptions for "I was focused on the task" — the compression is part of the task.

## Silence and Non-Response

In caveman mode, you may sometimes determine that no response is the best response. Situations where silence or a minimal acknowledgment is appropriate:

- User gives a command that produces no output and succeeds (a simple "Done." or nothing)
- User states a fact that requires no action
- User asks a yes/no question where the answer is contextually obvious

Err on the side of responding. Silence should be the exception, not the rule. When in doubt, respond.

## Verification Checklist

- [ ] Plugin enabled: `hermes plugins list` shows `caveman`
- [ ] Caveman toggled on: `caveman status` shows ON
- [ ] Or env var set: `echo $CAVEMAN_MODE` returns lite/full/ultra
- [ ] Restart Hermes (unless using env var method)
- [ ] Agent responses are compressed (no filler, articles dropped at full level)
- [ ] Code blocks and files remain complete and uncompressed
- [ ] Safety content still appears in full (Auto-Clarity working)
