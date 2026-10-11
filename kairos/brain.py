"""The optional Claude layer. Every caller has a heuristic fallback, so Kairos works offline;
with Claude connected, moment picking, prompt enhancement and feedback learning get sharper."""
from __future__ import annotations

import json

from . import config

_client = None
_last_error: str | None = None


def client():
    global _client, _last_error
    if _client is not None:
        return _client
    import os
    from pathlib import Path
    if not (config.api_key() or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_PROFILE")
            or (Path.home() / ".config" / "anthropic").exists()):
        _last_error = "Claude not connected: add an API key in Settings"
        return None
    try:
        import anthropic
    except ImportError:
        _last_error = "anthropic package not installed (pip install anthropic)"
        return None
    try:
        # api_key=None lets the SDK resolve ANTHROPIC_API_KEY, auth tokens or an `ant auth login` profile.
        _client = anthropic.Anthropic(api_key=config.api_key())
    except Exception as e:  # no credential source at all
        _last_error = str(e)
        return None
    return _client


def status() -> dict:
    c = client()
    return {"connected": c is not None, "model": config.settings()["model"], "error": None if c else _last_error}


def ask_json(system: str, user: str, schema: dict, effort: str = "high", max_tokens: int = 16000) -> dict | None:
    """One structured call. Returns parsed JSON, or None so the caller falls back to heuristics."""
    global _last_error
    c = client()
    if c is None:
        return None
    import anthropic
    try:
        resp = c.beta.messages.create(
            model=config.settings()["model"],
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
            # Raw, uncensored creator speech is the input; route any policy decline to a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        _last_error = "Claude key rejected"
        return None
    except anthropic.RateLimitError:
        _last_error = "Claude rate limit, used the built-in heuristics"
        return None
    except anthropic.APIStatusError as e:
        _last_error = f"Claude API error {e.status_code}"
        return None
    except anthropic.APIConnectionError:
        _last_error = "Could not reach Claude"
        return None
    except TypeError:  # the SDK found no credential source (no key, token or profile)
        _last_error = "Claude not connected: add an API key in Settings"
        return None
    if resp.stop_reason in ("refusal", "max_tokens"):
        _last_error = f"Claude stopped: {resp.stop_reason}"
        return None
    text = next((b.text for b in resp.content if b.type == "text"), "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        _last_error = "Claude returned invalid JSON"
        return None


def reset() -> None:
    """Drop the cached client (after the key changes in Settings)."""
    global _client
    _client = None
