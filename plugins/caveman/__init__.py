"""Caveman plugin — mechanical token-efficiency via llm_request middleware.

Injects caveman compression rules into the system message before every LLM call.
Toggle via:
  CAVEMAN_MODE=lite|full|ultra   (env var)
  caveman on|off                  (marker file at ~/.hermes/.caveman_active)

This is as reliable as the RTK plugin — the middleware fires on every LLM
request.  No behavioral self-enforcement needed.
"""

import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_CAVEMAN_MARKER = os.path.expanduser("~/.hermes/.caveman_active")
_CAVEMAN_LEVEL_MARKER = os.path.expanduser("~/.hermes/.caveman_level")

# --- Caveman instruction blocks per intensity level ------------------------

_CAVEMAN_LITE = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN LITE mode. Apply these rules to EVERY response:

1. DROP filler words: just, really, basically, actually, simply, very, quite.
2. DROP politeness padding: sure, certainly, of course, happy to.
3. DROP hedging: I think, perhaps, maybe, it seems like.
4. DROP concluding summaries and "hope this helps" sign-offs.
5. KEEP articles (a/an/the) and full sentences. Stay professional.
6. NEVER compress: code blocks, error messages, technical terms, file paths, commands.
7. For security warnings / destructive ops / legal content: write normally, then resume.

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
8. PREFER fragments over full sentences where meaning stays clear.
9. PREFER short synonyms: "big" not "extensive", "fix" not "implement a solution for".
10. USE pattern: [thing] [action] [reason]. [next step].
11. NEVER compress: code blocks (complete, valid), error messages (exact quotes),
    technical terms, function/API names, file paths, commands (copy-pasteable).
12. For security warnings / irreversible actions / legal content / ambiguous
    multi-step sequences: drop caveman temporarily, write clearly, then resume.

Example: NOT "Sure! I'd be happy to help with that. The issue is likely caused by..."
         YES "Bug in auth middleware. Token expiry check use < not <=. Fix:"

Goal: terse, technical, zero fluff. All substance. No ceremony.
"""

_CAVEMAN_ULTRA = """
[SYSTEM INSTRUCTION — ACTIVE THIS SESSION]
You are in CAVEMAN ULTRA mode. Apply these rules to EVERY response:

1. ABBREVIATE prose words: DB, auth, config, req, res, fn, impl, perf, mem, init.
2. STRIP conjunctions where possible.
3. USE arrows for causality: X → Y.
4. USE one word when one word is enough.
5. DROP everything from FULL mode (articles, filler, politeness, hedging, emoji,
   headings, summaries, sign-offs).
6. PREFER fragments.
7. NEVER abbreviate: code symbols, function names, API names, error strings,
   package names, file paths, commands.
8. For safety-critical content: write normally, then resume ultra.

Example: NOT "Connection pooling reuses open database connections..."
         YES "Pool = reuse DB conn. Skip handshake → fast under load."

Goal: maximum compression. Telegraphic. No syllable wasted.
"""

# Map level to instruction block
_LEVEL_INSTRUCTIONS = {
    "lite": _CAVEMAN_LITE,
    "full": _CAVEMAN_FULL,
    "ultra": _CAVEMAN_ULTRA,
}

# Shorter aliases
_LEVEL_ALIASES = {
    "l": "lite",
    "f": "full",
    "u": "ultra",
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
