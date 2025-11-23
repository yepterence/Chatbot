#!/usr/bin/python3

import asyncio
from ollama import AsyncClient

from models import StreamChunk

MODEL = "gemma3"

async def stream_chat(messages):
    """
    Streams dicts like {"delta": "..."} for the SSE endpoint to serialize.
    """

    client = AsyncClient()

    stream = await client.chat(
        model=MODEL,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.get('message', {}).get('content', {})
        response_data = StreamChunk(
            content=delta,
            finished=chunk.get('done', False)
        )
        yield f"data: {response_data.model_dump_json()}\n\n"

async def test_stream():
    test_messages = [{"role": "user", "content": "What is 2+2?"}]

    async for chunk in stream_chat(test_messages):
        print("SSE chunk: ", chunk)


if __name__ == "__main__":
    asyncio.run(test_stream())