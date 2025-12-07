#!/usr/bin/python3
import os
from sqlalchemy import Column, String, Text, DateTime, Integer, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime as dt


class Base(DeclarativeBase):
    pass

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at =  Column(DateTime, default=dt.now)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    chat_title = Column(String, nullable=False)


