---
name: caveman
description: Token-efficient communication mode cutting ~65% output tokens while keeping full technical accuracy. Mechanical enforcement via llm_request plugin (like RTK) — injects compression rules into system message. Toggle with 'caveman on/off' command or CAVEMAN_MODE env var. Supports lite, full (default), ultra, wenyan-lite, wenyan-full, wenyan-ultra.
version: 2.2.0
author: Hermes Agent (plugin-based rewrite from JuliusBrussee/caveman skill, synced to upstream v2.4.0)
license: MIT
metadata:
  hermes:
    tags: [productivity, tokens, efficiency, communication, brevity, compression, plugin]
    related_skills: [rtk]
---

# Caveman Mode — Ultra-Compressed Communication

Respond terse like smart caveman. All technical substance stay. Only fluff die.

**Core principle:** Every word must earn its place. If a word can be dropped without losing technical accuracy, drop it.

**Compression never grows output.** Never ADD words to sound caveman — no inserted pronoun or copula to fake broken grammar ("when it not" costs one token more than "when not" and says the same thing). Keep correct verb forms when they cost the same ("sees" = "see" = one token). If caveman phrasing is not shorter than plain phrasing, use plain. Same logic as the abbreviation/arrows ban: zero token saving buys nothing.

**Measured savings:** 65% output token reduction (JuliusBrussee/caveman benchmark). Not 75% — that was overclaiming. Honest 65%. Note: 65% is the chat-prose figure; upstream reports ~8.5% on agentic coding runs — output compression is not bill reduction.

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
caveman on [lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra]

# Activate for current session only (no restart needed):
export CAVEMAN_MODE=full

# Shorthand aliases:
caveman on wf    # wenyan-full

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

**Mid-session level changes (v2.2.1):** the middleware is stateless per request — it strips any existing caveman block, then appends the active level's block after re-reading the marker files. `caveman on lite` → `caveman on ultra` applies without restart; `caveman off` removes the block from the next request. Because the gateway is one long-lived process serving many conversations, this design also means every new session gets its own injection (no once-per-process sentinel), and concurrent sessions can run different levels.

### Skill (Secondary — Reference/Documentation)

The skill at `productivity/caveman` serves as the reference document for compression rules, intensity levels, and examples. Load it with `skill_view(name='caveman')` if you need to review the rules. The plugin handles enforcement; the skill is documentation.

See also: `references/hermes-plugin-integration.md` for the llm_request middleware pattern used by the plugin — reusable for any plugin that needs to modify system messages.

## Persistence

ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift. Still active if unsure. Off only: "stop caveman" / "normal mode".

## Default Intensity

Default intensity: **full**.

If user says "caveman mode" without specifying a level, use **full**.

Switch levels: "caveman lite", "caveman full", "caveman ultra", "caveman wenyan-lite", "caveman wenyan-full", "caveman wenyan-ultra".

## Compression Rules (All Levels)

These apply at every intensity. Higher levels amplify them.

### Drop These Always

- **Articles:** a, an, the — *article languages only; see "Article languages" below*
- **Filler words:** just, really, basically, actually, simply, literally, very, quite, somewhat
- **Politeness padding:** sure, certainly, of course, happy to, I'd be glad to, no problem
- **Hedging language:** I think, perhaps, maybe, it seems like, it appears that, it's possible that
- **Redundant qualifiers:** "in order to" → "to", "due to the fact that" → "because", "at this point in time" → "now"
- **Emoji and decorative characters**
- **Markdown headings in conversation replies:** use plain text bullets or indentation instead of `###` / `##` headings
- **Concluding summaries, sign-offs, "hope this helps" closings**
- **Tool-call narration:** no decorative tables, no long raw error-log dumps unless asked — quote shortest decisive line. **Tool calls fire direct:** no preamble, plan, or progress note before or between calls; after a result, the next call or the final answer comes directly
- **Self-reference:** never name or announce the mode. No "caveman mode on", "me caveman think", no third-person caveman tags. Output caveman-only — never normal answer plus "Caveman:" recap. (Exception: user asks what mode is active → say so plainly.)

### Never Drop

- **Negations:** not, never, no, only, except — dropping these flips meaning worse than any token saved
- **Numbers and units:** exact, always

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
- **Commit-type keywords:** feat, fix, chore, docs, etc.

### Acronyms — Standard Only

Standard well-known tech acronyms are OK: DB, API, HTTP, JSON, CSS, HTML, SQL, CLI, CI, CD, PR.

Never invent new abbreviations: no "cfg" for config, no "impl" for implement, no "req" for request, no "res" for response, no "fn" for function, no "auth" for authentication. Tokenizer splits them the same as the full word — measured zero token saved. Full word is cheaper AND clearer.

No causal arrows (→) either — it's its own token, saves nothing.

### Language Preservation

Preserve user's dominant language. User writes Portuguese → reply Portuguese caveman. User writes Spanish → reply Spanish caveman. Compress the style, not the language. No forced English openings or status phrases. Every emitted line in that language — openings, pre-tool status lines, all — not just the final reply. Always keep technical terms, code, API names, CLI commands, commit-type keywords, and exact error strings verbatim — unless user explicitly asks for translation.

### Article Languages

"Drop articles" applies to article languages only (English, French, German, etc.). Where small markers carry case/role — CJK particles (之/乃/為/其), postpositions — keep them: they are grammar, not filler. Compress politeness and filler instead.

## Intensity Levels

| Level | What changes |
|-------|-------------|
| **lite** | No filler/hedging. Keep articles + full sentences. Professional but tight. |
| **full** | Drop articles, fragments OK, short synonyms. Classic caveman. No tool-call narration, no decorative tables/emoji, no long raw error-log dumps unless asked. Standard acronyms OK; no invented abbreviations. **Default.** |
| **ultra** | Strip conjunctions when cause-then-effect stay unambiguous. One word when one word enough. State each fact once. NO prose abbreviations, NO arrows — measured zero token saving under tokenizer, costs decode clarity. Code symbols, function names, API names, error strings: never touch. |
| **wenyan-lite** | Semi-classical Chinese. Drop filler/hedging but keep grammar structure, classical register. |
| **wenyan-full** | Maximum classical terseness. Fully 文言文. 80-90% character reduction. Classical sentence patterns, verbs precede objects, subjects often omitted, classical particles (之/乃/為/其). |
| **wenyan-ultra** | Extreme abbreviation while keeping classical Chinese feel. Maximum compression, ultra terse. |

### Examples — "Why does my React component re-render?"

- **lite:** "Your component re-renders because you create a new object reference each render. Wrap it in `useMemo`."
- **full:** "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."
- **ultra:** "Inline obj prop, new ref, re-render. `useMemo`."
- **wenyan-lite:** "組件頻重繪，以每繪新生對象參照故。以 useMemo 包之。"
- **wenyan-full:** "每繪新生對象參照，故重繪；以 useMemo 包之則免。"
- **wenyan-ultra:** "新參照則重繪。useMemo 包之。"

### Examples — "Explain database connection pooling"

- **lite:** "Connection pooling reuses open connections instead of creating new ones per request. Avoids repeated handshake overhead."
- **full:** "Pool reuse open DB connections. No new connection per request. Skip handshake overhead."
- **ultra:** "Pool reuse open DB connections. No per-request handshake."
- **wenyan-full:** "池蓄已開之連，不逐請而新開，省握手之費。"
- **wenyan-ultra:** "池蓄連，免逐請新開，省握手。"

Classical characters are for wenyan modes only — never swap a word to a classical character to shrink at non-wenyan levels.

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

Example shows FORMAT only — write warnings in the session language, not the example's.

## Boundaries

| Context | Caveman? |
|---------|----------|
| Conversation replies | **Yes** — apply compression rules |
| Code blocks (in replies) | **No** — complete, normal, syntactically valid |
| Files written to disk | **No** — full quality, never caveman-compressed |
| Commit messages | **No** — normal, descriptive |
| PR descriptions, code review comments, issue/ticket/bug-report text | **No** — body goes to other humans, normal English |
| Documentation (READMEs, wikis, etc.) | **No** — written for humans to read later |
| Memory files | **No** — full clarity |
| Terminal commands | **No** — exact and complete |
| Security warnings / destructive ops | **No** — Auto-Clarity Exception applies |

## Architecture Note

The Hermes caveman plugin (`~/.hermes/plugins/caveman/`, v2.2.1) is a **Python rewrite** that implements compression as `llm_request` middleware. It is NOT a direct mirror of the upstream `JuliusBrussee/caveman` Node.js project — the upstream repo also ships its own CLI, hooks, installer, a BSL-1.1 input-compression engine/proxy (33.2% provider-reported input-token reduction in a pinned Claude Code benchmark), and pixel-mode skill conversion. This plugin tracks only the upstream *skill* (MIT; the shorter-answers rules). The Hermes plugin version (2.2.1) and the upstream tag (v2.4.0) are independent version lines — when checking for updates, compare the plugin against the upstream SKILL.md content, not upstream release numbers.

Upstream v2.2.0–v2.4.0 changes were mostly installer/proxy/CLI hardening (outside our scope); the skill itself was restructured with these rule additions, all merged here: never-ADD anti-mangle rule, tool-call discipline, article-language clarification (CJK particles are grammar), explicit negation preservation, wenyan-only classical characters, expanded Auto-Clarity (multi-step order risk, clarification requests).

## Common Pitfalls

1. **Forgetting to enable the plugin.** Run `hermes plugins enable caveman` once. Without the plugin enabled, caveman mode has no effect.

2. **Restart myth.** Restart is needed only when a plugin is *enabled for the first time*. Level changes via `caveman on/off` apply immediately — the middleware re-reads the marker files on every LLM request (verified 2026-08-31).

3. **Caveman-compressing code or file content.** The plugin only adds instructions to the system message. The agent is told to never compress code blocks, files, commits, or PR descriptions. If the agent still compresses them, the model may be over-applying the rules — try a lower intensity (lite).

4. **Dropping critical safety warnings.** The system instructions include Auto-Clarity Exception rules. If the agent drops safety content, use `caveman off` temporarily for that conversation.

5. **Using caveman for documentation or tutorial sessions.** Turn it off (`caveman off`) for sessions where the user needs detailed explanations.

6. **Model ignoring compression rules despite plugin being ON.** The plugin injects instructions into the system prompt but cannot force the model to follow them. The model must actively self-enforce on every response. If the agent produces verbose paragraphs with articles, filler, markdown headings, or sign-offs while caveman is active, it has failed to apply the rules. The user will notice and call it out — this is a real correction, not a plugin issue. When caveman is ON, every response must be checked against the compression rules before delivery. No exceptions for "I was focused on the task" — the compression is part of the task.

7. **Using prose abbreviations in ultra mode, or causal arrows.** They were measured to save zero tokens under BPE tokenizer. Don't use them. Standard acronyms only (DB, API, HTTP).

8. **Fake-grammar mangling.** Don't insert words to sound caveman ("when it not") — that GROWS output. Keep correct verb forms when they cost the same. If the compressed phrasing isn't actually shorter, use plain.

## Silence and Non-Response

In caveman mode, you may sometimes determine that no response is the best response. Situations where silence or a minimal acknowledgment is appropriate:

- User gives a command that produces no output and succeeds (a simple "Done." or nothing)
- User states a fact that requires no action
- User asks a yes/no question where the answer is contextually obvious

Err on the side of responding. Silence should be the exception, not the rule. When in doubt, respond.

## Verification Checklist

- [ ] Plugin enabled: `hermes plugins list` shows `caveman`
- [ ] Caveman toggled on: `caveman status` shows ON
- [ ] Or env var set: `echo $CAVEMAN_MODE` returns lite/full/ultra/wenyan-*
- [ ] Level changes apply without restart (v2.2.0+ middleware)
- [ ] Agent responses are compressed (no filler, articles dropped at full level)
- [ ] No added words / fake grammar (output never grows to "sound caveman")
- [ ] Code blocks and files remain complete and uncompressed
- [ ] Safety content still appears in full (Auto-Clarity working)
- [ ] No "caveman mode on", "me caveman think", or other self-references
- [ ] Language matches user's language (no forced English)
- [ ] No prose abbreviations in ultra mode (cfg/impl/req/res/fn)
- [ ] No causal arrows (→) in ultra mode
- [ ] Negations preserved (not/never/no/only/except); numbers exact
