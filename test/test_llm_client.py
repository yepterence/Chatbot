#!/usr/bin/python3

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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

@pytest.mark.asyncio
async def test_multi_turn_chat_keeps_context():
    """Test that a multi-turn prompt is forwarded to the provider in full and in order."""
    provider = make_fake_provider([], response_text="Python Basics Explained")
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Python briefly"},
        {"role": "assistant", "content": "Python is a high-level language."},
        {"role": "user", "content": "What makes it high-level?"},
    ]
    chat = Chat("test-101", prompt, provider)

    title = await chat.generate_title()

    assert title == "Python Basics Explained"
    provider.generate.assert_called_once()
    sent_messages = provider.generate.call_args.args[0]

    # generate_title prepends its own system prompt, so the original
    # conversation should appear intact right after it, in order.
    assert [m.role for m in sent_messages] == ["system"] + [m["role"] for m in prompt]
    assert [m.content for m in sent_messages[1:]] == [m["content"] for m in prompt]


class _FakeChatHistory:
    def __init__(self, id_: int, title: str) -> None:
        self.id = id_
        self.chat_title = title


@pytest.mark.asyncio
async def test_persist_chat_reuses_existing_session_across_turns():
    """A follow-up turn in the same conversation must append to the existing
    ChatHistory row instead of creating a new session/title."""
    created_sessions: list[_FakeChatHistory] = []

    async def fake_create_chat_session(title):
        history = _FakeChatHistory(id_=len(created_sessions) + 1, title=title)
        created_sessions.append(history)
        return history

    async def fake_get_chat_messages(chat_id):
        return next(
            (session for session in created_sessions if session.id == chat_id),
            None,
        )

    repo_instance = MagicMock()
    repo_instance.create_chat_session = AsyncMock(side_effect=fake_create_chat_session)
    repo_instance.get_chat_messages = AsyncMock(side_effect=fake_get_chat_messages)
    repo_instance.add_message = AsyncMock()

    fake_session_cm = MagicMock()
    fake_session_cm.__aenter__ = AsyncMock(return_value=MagicMock())
    fake_session_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("api.llm_client.session_context", return_value=fake_session_cm), \
         patch("api.llm_client.ChatRepo", return_value=repo_instance):
        provider = make_fake_provider([], response_text="Python basics")

        # Turn 1: user starts a brand new conversation.
        turn_1_prompt = [{"role": "user", "content": "Explain Python briefly"}]
        chat_turn_1 = Chat("exec-1", turn_1_prompt, provider)
        chat_turn_1.finalized_message = "Python is a high-level language."
        history_id = await chat_turn_1.persist_chat(title="Python basics")

        # Turn 2: same conversation, continuing the persisted session.
        turn_2_prompt = turn_1_prompt + [
            {"role": "assistant", "content": "Python is a high-level language."},
            {"role": "user", "content": "What makes it high-level?"},
        ]
        chat_turn_2 = Chat(
            "exec-2",
            turn_2_prompt,
            provider,
            chat_history_id=history_id,
        )
        chat_turn_2.finalized_message = "It abstracts away memory management."
        await chat_turn_2.persist_chat()

    assert len(created_sessions) == 1
    assert history_id == created_sessions[0].id
    repo_instance.create_chat_session.assert_awaited_once()
    assert repo_instance.add_message.await_count == 4
