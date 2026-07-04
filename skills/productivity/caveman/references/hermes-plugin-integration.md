# Hermes llm_request Middleware — Caveman Integration Pattern

How the caveman plugin hooks into Hermes Agent's LLM request pipeline.
Same pattern works for any plugin that needs to modify the system message
or API request before the provider sees it.

## Where Middleware Fires

In `agent/conversation_loop.py` (~line 876), before every LLM API call:

```python
from hermes_cli.middleware import apply_llm_request_middleware

_llm_request_mw = apply_llm_request_middleware(
    api_kwargs,           # The full provider request dict (includes "messages" key)
    task_id=...,
    session_id=...,
    model=...,
    ...
)
api_kwargs = _llm_request_mw.payload   # Modified payload after middleware
```

`api_kwargs` at this point contains the fully assembled request: system
message, conversation history, tool schemas, model params. Middleware gets
to rewrite it before the provider API call.

## Middleware Contract

The middleware callback receives `**kwargs` with at minimum:
- `request` (dict): The provider request payload with `messages` key

It must return `{"request": modified_request}` — the `request` key is
required. Middleware can be chained: each middleware's output becomes the
next one's input.

```python
def _caveman_middleware(**kwargs):
    request = kwargs.get("request", {})
    messages = request.get("messages", [])
    # Find and modify the system message
    for msg in messages:
        if msg.get("role") == "system":
            msg["content"] += "\n\n[caveman rules here]"
            break
    return {"request": request}
```

## Registration

In the plugin's `register(ctx)` function:

```python
def register(ctx):
    ctx.register_middleware("llm_request", _caveman_middleware)
```

Supported middleware kinds (from `hermes_cli/middleware.py`):
- `llm_request` — rewrite provider request before API call
- `llm_execution` — wrap the actual API call
- `tool_request` — rewrite tool arguments before execution
- `tool_execution` — wrap tool execution

## Plugin Manifest (plugin.yaml)

```yaml
name: caveman
version: "1.0.0"
description: Description here
author: Author
hooks: []           # Empty is fine — middleware is registered in register()
provides_hooks: []  # Same
# The 'middleware' field below is custom — Hermes ignores unknown fields
# but it's good documentation for humans reading the manifest
middleware:
  - llm_request
```

The `hooks` and `provides_hooks` fields are for lifecycle hooks (pre_tool_call,
post_tool_call, etc.). Middleware is registered programmatically in `register()`,
not via plugin.yaml fields.

## Prompt Caching Impact

Injecting content into the system message via middleware adds ~320 tokens
to the system prompt. This is negligible compared to the ~65-80% total
savings from RTK + Caveman, but the middleware MUST inject once per session
(use a flag like `_CAVEMAN_INJECTED`) to avoid doubling on every turn.

The caveman plugin uses a module-level global `_CAVEMAN_INJECTED` that is:
- Set True after first injection
- Reset to False when caveman is toggled off (detected in the next middleware call)
- Resets per process (new Hermes session = fresh Python process in most setups)

## Verified Against

- Hermes Agent as of June 2026
- `agent/conversation_loop.py` lines 876-896
- `hermes_cli/middleware.py` — `apply_llm_request_middleware()`, `VALID_MIDDLEWARE`
- `hermes_cli/plugins.py` line 958 — `register_middleware()`
- `tests/hermes_cli/test_plugins.py` — middleware tests confirming `llm_request` is valid
