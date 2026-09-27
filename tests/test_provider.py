"""Focused tests for provider selection without making network requests."""

import pytest

from src.mcp_server.ai import provider


@pytest.mark.asyncio
async def test_watsonx_provider_runs_sdk_call_off_event_loop(monkeypatch):
    monkeypatch.setattr(provider, "LLM_PROVIDER", "watsonx")
    monkeypatch.setattr(provider, "_watsonx_chat_completion", lambda *args, **kwargs: "native response")

    result = await provider._chat_completion("system", "user")

    assert result == "native response"


@pytest.mark.asyncio
async def test_unknown_provider_fails_with_actionable_error(monkeypatch):
    monkeypatch.setattr(provider, "LLM_PROVIDER", "unknown")

    with pytest.raises(RuntimeError, match="LLM_PROVIDER"):
        await provider._chat_completion("system", "user")
