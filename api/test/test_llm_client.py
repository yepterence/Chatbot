#!/usr/bin/python3

import pytest
import asyncio
import pytest_asyncio
from api.llm_client import stream_chat

@pytest.mark.asyncio
async def test_stream_chat_valid_prompt():
    prompt = [{"role":"user","content":"What is 2 + 2?"}]
    stream_response = stream_chat(prompt)
    _chunks = []
    async for chunk in stream_response:
        assert isinstance(chunk, str)
        _chunks.append(chunk)
    final_text = "".join(_chunks)
    assert "4" in final_text
