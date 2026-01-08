#!/usr/bin/python3

from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class CancelRequest(BaseModel):
    chat_id: str
    
class StreamChunk(BaseModel):
    content: str
    finished: bool
    source: Optional[str] = None
