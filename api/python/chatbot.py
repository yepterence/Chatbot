import asyncio
import json
from typing import AsyncGenerator, List, Dict
from ollama import AsyncClient

MODEL = "gemma3"

async def stream_chat(messages: List[Dict]) -> AsyncGenerator[Dict, None]:
    """
    Streams chat responses token-by-token from local Ollama (gemma3).
    This function yields dicts: {"delta": "..."} and {"done": True}.
    """

    client = AsyncClient()

    # Stream tokens from Ollama
    stream = await client.chat(
        model=MODEL,
        messages=messages,
        stream=True,
    )

    async for part in stream:
        delta = part.get("message", {}).get("content", "")
        if delta:
            yield f"data: {json.dumps({'delta': delta})}\n\n"

    yield "data: {\"done\": true}\n\n"
