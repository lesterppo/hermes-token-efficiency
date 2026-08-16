"""Caveman plugin — mechanical token-efficiency via llm_request middleware.

Injects caveman compression rules into the system message before every LLM call.
Toggle via:
  CAVEMAN_MODE=lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra  (env var)
  caveman on|off [lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra]  (marker file)

Based on upstream JuliusBrussee/caveman v2.0.0 skill — honest 65% measured output reduction.
Rules validated against tokenizer behaviour: prose abbreviations and causal arrows
measured as zero token savings; removed from ultra mode for decode clarity.

This is as reliable as the RTK plugin — the middleware fires on every LLM
request. No behavioral self-enforcement needed.
"""

import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_CAVEMAN_MARKER = os.path.expanduser("~/.hermes/.caveman_active")
_CAVEMAN_LEVEL_MARKER = os.path.expanduser("~/.hermes/.caveman_level")

# --- Caveman instruction blocks per intensity level ------------------------
# Rules validated against the upstream JuliusBrussee/caveman skill (v2.0.0).
# Key corrections vs earlier versions:
#   - ULTRA: NO prose abbreviations (cfg/impl/req/res/fn/auth) — measured zero
#     token saving under BPE tokenizer; costs decode clarity.
#   - ULTRA: NO causal arrows (→) — own token, saves nothing.
#   - Standard well-known acronyms OK (DB/API/HTTP); never invent new ones.
#   - No self-reference: never name or announce the style.
#   - Preserve user's dominant language — compress style, not language.

_CAVEMAN_LITE = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN LITE mode. Apply these rules to EVERY response:

1. DROP filler words: just, really, basically, actually, simply, very, quite.
2. DROP politeness padding: sure, certainly, of course, happy to.
3. DROP hedging: I think, perhaps, maybe, it seems like.
4. DROP concluding summaries and "hope this helps" sign-offs.
5. KEEP articles (a/an/the) and full sentences. Stay professional.
6. NEVER compress: code blocks, error messages, technical terms, file paths, commands.
7. NEVER name or announce the mode. No "caveman mode on", no third-person tags.
8. For security warnings / destructive ops / legal content: write normally, then resume.

Goal: tight, professional responses with zero fluff. Every word earns its place.
"""

_CAVEMAN_FULL = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN FULL mode. Apply these rules to EVERY response:

1. DROP articles: a, an, the.
2. DROP filler words: just, really, basically, actually, simply, very, quite.
3. DROP politeness padding: sure, certainly, of course, happy to.
4. DROP hedging language: I think, perhaps, maybe, it seems like.
5. DROP emoji and decorative characters.
6. DROP markdown headings in replies (use plain text or bullets).
7. DROP concluding summaries, sign-offs, "hope this helps" closings.
8. DROP tool-call narration: no decorative tables, no long raw error-log dumps
   unless asked — quote shortest decisive line.
9. PREFER fragments over full sentences where meaning stays clear.
10. PREFER short synonyms: "big" not "extensive", "fix" not "implement a solution for".
11. Standard well-known tech acronyms OK: DB, API, HTTP, JSON, CSS, HTML, SQL, CLI,
    CI, CD, PR. Never invent new abbreviations — "config" not "cfg", "impl" not
    "impl", "function" not "fn". Tokenizer splits them same: zero token saved.
12. USE pattern: [thing] [action] [reason]. [next step].
13. NEVER compress: code blocks (complete, valid), error messages (exact quotes),
    technical terms, function/API names, file paths, commands (copy-pasteable).
14. NEVER name or announce the mode. No "caveman mode on", no "me caveman think",
    no third-person caveman tags. Output caveman-only — never normal answer plus
    "Caveman:" recap.
15. PRESERVE user's dominant language. User writes Portuguese → reply Portuguese
    caveman. Compress the style, not the language. No forced English openings.
16. For security warnings / irreversible actions / legal content / ambiguous
    multi-step sequences: drop caveman temporarily, write clearly, then resume.

Example: NOT "Sure! I'd be happy to help with that. The issue is likely caused by..."
         YES "Bug in auth middleware. Token expiry check use < not <=. Fix:"

Goal: terse, technical, zero fluff. All substance. No ceremony.
"""

_CAVEMAN_ULTRA = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN ULTRA mode. Apply these rules to EVERY response:

1. DROP everything from FULL mode (articles, filler, politeness, hedging, emoji,
   headings, summaries, sign-offs, tool-call narration).
2. STRIP conjunctions when cause-then-effect stays unambiguous.
3. USE one word when one word is enough. State each fact once.
4. PREFER fragments.
5. NEVER use prose abbreviations: no "cfg" for config, no "impl" for implement,
   no "req" for request, no "res" for response, no "fn" for function, no "auth"
   for authentication, no "perf" for performance, no "mem" for memory, no
   "init" for initialize. Tokenizer splits them same as full word — measured
   zero token saved. Full word cheaper AND clearer.
6. NEVER use causal arrows (→). It's its own token — saves nothing, costs clarity.
7. NEVER compress: code blocks, error messages (exact quotes), technical terms,
   function/API names, file paths, commands, commit-type keywords (feat/fix/...).
8. Standard acronyms OK where universally recognized (DB, API, HTTP, JSON, CSS,
   HTML, SQL, CLI, CI, CD, PR).
9. NEVER name or announce the mode. No self-reference.
10. PRESERVE user's dominant language — compress style, not language.
11. For safety-critical content: write normally, then resume ultra.

Example: NOT "Connection pooling reuses open database connections..."
         YES "Pool reuse open DB connections. No per-request handshake."

Goal: maximum compression. Telegraphic. No syllable wasted.
"""

_CAVEMAN_WENYAN_LITE = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN WENYAN-LITE mode (半文言). Apply these rules to EVERY response:

1. Use semi-classical Chinese register.
2. Drop filler/hedging but keep grammar structure.
3. Keep classical particles where natural (之/乃/為/其/故/以).
4. NEVER compress code blocks, error messages, technical terms, API names, commands.
5. NEVER name or announce the mode.
6. For safety-critical content: write clearly in modern Chinese, then resume.

Goal: classical elegance with modern comprehensibility.
"""

_CAVEMAN_WENYAN_FULL = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN WENYAN-FULL mode (全文言). Apply these rules to EVERY response:

1. Respond in fully classical Chinese (文言文). 80-90% character reduction.
2. Use classical sentence patterns: verbs precede objects, subjects often omitted.
3. Use classical particles: 之/乃/為/其/故/以/而/則/者/也.
4. Maximum terseness. Every character must earn its place.
5. NEVER compress code blocks, error messages (exact quotes), technical terms,
   API names, file paths, commands — these stay in original language.
6. NEVER name or announce the mode.
7. For safety-critical content: write clearly in modern Chinese, then resume.

Goal: pure classical Chinese. No modern filler. 文言文.
"""

_CAVEMAN_WENYAN_ULTRA = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN WENYAN-ULTRA mode (極文言). Apply these rules to EVERY response:

1. Extreme classical Chinese abbreviation while keeping classical feel.
2. Maximum compression. Ultra terse. 文言文極簡.
3. Drop all non-essential characters. Single-character words where possible.
4. Classical particles only when they carry meaning.
5. NEVER compress code blocks, error messages (exact quotes), technical terms,
   API names, file paths, commands — these stay in original language.
6. NEVER name or announce the mode.
7. For safety-critical content: write clearly in modern Chinese, then resume.

Goal: densest possible classical Chinese. 極簡文言.
"""

# Map level to instruction block
_LEVEL_INSTRUCTIONS = {
    "lite": _CAVEMAN_LITE,
    "full": _CAVEMAN_FULL,
    "ultra": _CAVEMAN_ULTRA,
    "wenyan-lite": _CAVEMAN_WENYAN_LITE,
    "wenyan-full": _CAVEMAN_WENYAN_FULL,
    "wenyan-ultra": _CAVEMAN_WENYAN_ULTRA,
}

# Shorter aliases
_LEVEL_ALIASES = {
    "l": "lite",
    "f": "full",
    "u": "ultra",
    "wl": "wenyan-lite",
    "wf": "wenyan-full",
    "wu": "wenyan-ultra",
}

# Sentinel to prevent re-injection every call
_CAVEMAN_INJECTED = False


def register(ctx):
    """Register llm_request middleware."""
    ctx.register_middleware("llm_request", _caveman_middleware)
    logger.info("Caveman plugin registered (llm_request middleware)")


def _get_active_level() -> Optional[str]:
    """Check if caveman mode is active and return the intensity level."""
    # 1. Check env var (highest priority, session-scoped)
    env_level = os.environ.get("CAVEMAN_MODE", "").strip().lower()
    if env_level in _LEVEL_ALIASES:
        env_level = _LEVEL_ALIASES[env_level]
    if env_level in _LEVEL_INSTRUCTIONS:
        return env_level

    # 2. Check marker files
    if os.path.exists(_CAVEMAN_MARKER):
        # Read level from level marker file
        if os.path.exists(_CAVEMAN_LEVEL_MARKER):
            try:
                with open(_CAVEMAN_LEVEL_MARKER) as f:
                    file_level = f.read().strip().lower()
                if file_level in _LEVEL_ALIASES:
                    file_level = _LEVEL_ALIASES[file_level]
                if file_level in _LEVEL_INSTRUCTIONS:
                    return file_level
            except Exception:
                pass
        return "full"  # Default level when marker exists

    return None


def _caveman_middleware(**kwargs: Any) -> Dict[str, Any]:
    """Middleware that injects caveman compression rules into the system message."""
    global _CAVEMAN_INJECTED

    request = kwargs.get("request", {})
    if not isinstance(request, dict):
        return {"request": request}

    level = _get_active_level()
    if level is None:
        # Caveman not active — but if it was previously injected,
        # we're in a new session now, reset the flag
        _CAVEMAN_INJECTED = False
        return {"request": request}

    instruction = _LEVEL_INSTRUCTIONS.get(level)
    if not instruction:
        return {"request": request}

    messages = request.get("messages")
    if not isinstance(messages, list) or not messages:
        return {"request": request}

    # Find the system message (usually messages[0])
    system_idx = None
    for i, msg in enumerate(messages):
        if isinstance(msg, dict) and msg.get("role") == "system":
            system_idx = i
            break

    if system_idx is None:
        # No system message — prepend one
        messages.insert(0, {"role": "system", "content": instruction.strip()})
        _CAVEMAN_INJECTED = True
        logger.debug("Caveman: prepended system message (level=%s)", level)
        return {"request": request}

    # Append to existing system message (only once per session)
    if _CAVEMAN_INJECTED:
        # Already injected — don't double-inject (content is already there)
        return {"request": request}

    system_msg = messages[system_idx]
    content = system_msg.get("content", "")

    # Inject caveman rules after the existing system prompt
    system_msg["content"] = content + "\n\n" + instruction.strip()
    _CAVEMAN_INJECTED = True
    logger.debug("Caveman: injected into system message (level=%s, idx=%d)", level, system_idx)

    return {"request": request}
