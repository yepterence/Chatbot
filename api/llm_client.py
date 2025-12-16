#!/usr/bin/python3

from ollama import AsyncClient, ChatResponse, chat

from .models import StreamChunk
from .logger import get_logger
from db.crud import create_chat_session, add_message

logger = get_logger(__name__)
logger.setLevel("DEBUG")
MODEL = "gemma3"

async def stream_chat(messages,):
    """
    Streams dicts like {"data": { ... }} for the SSE endpoint to serialize.
    """

    client = AsyncClient()

    stream = await client.chat(
        model=MODEL,
        messages=messages,
        stream=True,
    )
    logger.info("Chat activated")
    async for chunk in stream:
        delta = chunk['message']['content']
        logger.debug("Received chunk: %s", delta)
        response_data = StreamChunk(
            content=delta,
            finished=chunk.get('done', False)
        )
        logger.debug("Streaming chunk: %s", response_data)
        yield f"data: {response_data.model_dump_json()}\n\n"

async def write_msg_to_db(table, payload):
    pass

async def generate_title(messages):
    pass

async def non_stream_response(messages):
    response: ChatResponse = chat(
        model=MODEL,
        messages=messages,
        stream=False,
    )
    return response["message"]["content"]
