#!/usr/bin/python3

import json
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
        assert chunk.startswith("data:")
        _dict = json.loads(chunk[len("data:"):].strip())
        _chunks.append(_dict.get("content"))
    final_text = "".join(_chunks)
    assert "2 + 2 = 4" in final_text
