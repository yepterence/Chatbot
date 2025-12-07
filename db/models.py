#!/usr/bin/python3

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime as dt


class Base(DeclarativeBase):
    pass

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at =  Column(DateTime, default=dt.now)
    chat_history_id_fk = Column(Integer, ForeignKey("chat_history.id"))
    chat_history = relationship("ChatHistory", back_populates="chat_messages")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    chat_title = Column(String, nullable=False)
    chat_messages_id_fk = Column(Integer, ForeignKey("chat_messages.id"))
    chat_messages = relationship("ChatMessages", back_populates="chat_history")
