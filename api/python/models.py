#!/usr/bin/python3

from typing import Dict, List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt:str

class StreamChunk(BaseModel):
    content: str
    finished: bool
    source: Optional[str] = None
