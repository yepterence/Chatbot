#!/usr/bin/python3

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from api.llm.base import LLMChunk, LLMResponse
from api.llm_client import Chat


def make_fake_provider(chunks: list[LLMChunk], response_text: str = ""):
    """Build a minimal fake LLMProvider for testing without a live LLM."""

    async def _stream_gen(*args, **kwargs):
        for chunk in chunks:
            yield chunk

    provider = MagicMock()
    provider.stream = MagicMock(side_effect=_stream_gen)
    provider.generate = AsyncMock(return_value=LLMResponse(text=response_text))
    return provider


@pytest.mark.asyncio
async def test_stream_chat_yields_sse_formatted_strings():
    chunks = [
        LLMChunk(delta="Hello", finished=False),
        LLMChunk(delta=" world", finished=True),
    ]
    provider = make_fake_provider(chunks)
    prompt = [{"role": "user", "content": "Hi"}]
    chat = Chat("test-123", prompt, provider)

    collected = []
    async for line in chat.stream_chat():
        assert isinstance(line, str)
        assert line.startswith("data:")
        payload = json.loads(line[len("data:"):].strip())
        collected.append(payload["content"])

    assert collected == ["Hello", " world"]


@pytest.mark.asyncio
async def test_generate_title_uses_provider():
    provider = make_fake_provider([], response_text="What is Python")
    prompt = [{"role": "user", "content": "Explain Python briefly"}]
    chat = Chat("test-456", prompt, provider)
    title = await chat.generate_title()
    assert title == "What is Python"
    provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_finalize_streams_builds_message():
    chunks = [
        LLMChunk(delta="2 + 2 = 4", finished=False),
        LLMChunk(delta=".", finished=True),
    ]
    provider = make_fake_provider(chunks)
    prompt = [{"role": "user", "content": "What is 2 + 2?"}]
    chat = Chat("test-789", prompt, provider)

    async for _ in chat.stream_chat():
        pass

    await chat.finalize_streams()
    assert chat.finalized_message == "2 + 2 = 4."
