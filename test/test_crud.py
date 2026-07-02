#!/usr/bin/python3


import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories import ChatRepo
from api.database import ChatHistory, ChatMessage


def make_mock_session():
    """Return a minimal AsyncSession mock that satisfies ChatRepo's expectations."""
    session = MagicMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_create_chat_session():
    session = make_mock_session()

    async def fake_flush():
        # Simulate the DB assigning an id after flush
        pass

    session.flush = AsyncMock(side_effect=fake_flush)

    repo = ChatRepo(session)
    result = await repo.create_chat_session(title="Test Chat")

    assert isinstance(result, ChatHistory)
    assert result.chat_title == "Test Chat"
    session.add.assert_called_once_with(result)
    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_message():
    session = make_mock_session()
    repo = ChatRepo(session)

    result = await repo.add_message(
        chat_id=1,
        role="user",
        content="Hello",
        created_at=None,
    )

    assert isinstance(result, ChatMessage)
    assert result.role == "user"
    assert result.content == "Hello"
    assert result.chat_history_id_fk == 1
    session.add.assert_called_once_with(result)
    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_chat_messages_invalid_id():
    session = make_mock_session()
    repo = ChatRepo(session)

    result = await repo.get_chat_messages("not-an-int")

    assert result is None


@pytest.mark.asyncio
async def test_get_chat_history_returns_all():
    session = make_mock_session()

    fake_history = [ChatHistory(chat_title="A"), ChatHistory(chat_title="B")]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = fake_history
    session.execute = AsyncMock(return_value=mock_result)

    repo = ChatRepo(session)
    result = await repo.get_chat_history()

    assert result == fake_history
    session.execute.assert_awaited_once()
