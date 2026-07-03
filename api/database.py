#!/usr/bin/python3

from contextlib import asynccontextmanager
import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from api.config import Settings
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime as dt
from api.logger import get_logger

logger = get_logger("db_setup")


def get_database_url() -> str:
    # CHANGED: prefer a single DATABASE_URL when present. This matches Alembic's
    # usual configuration style and avoids requiring db_* fields in every context.
    if database_url := os.getenv("DATABASE_URL"):
        return database_url

    try:
        settings = Settings()
    except Exception as exc:
        raise RuntimeError(
            "Database configuration is required. Set DATABASE_URL, or set all "
            "of db_user, db_pass, db_name, db_host, and db_port."
        ) from exc

    return (
        f"postgresql+asyncpg://{settings.db_user}:"
        f"{settings.db_pass}@{settings.db_host}:"
        f"{settings.db_port}/{settings.db_name}"
    )


class Base(DeclarativeBase):
    pass

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at =  Column(DateTime(timezone=True), default=dt.now, nullable=False)
    chat_history_id_fk = Column(Integer, ForeignKey("chat_history.id"))
    
    chat_history = relationship("ChatHistory", back_populates="chat_messages")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    chat_title = Column(String, nullable=False)

    chat_messages = relationship("ChatMessage", 
                                 back_populates="chat_history",
                                 cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="chat_history", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    status = Column(String, nullable=False)
    agent_mode = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=dt.now, nullable=False)
    chat_history_id_fk = Column(Integer, ForeignKey("chat_history.id"))

    chat_history = relationship("ChatHistory", back_populates="interactions")
    agent_traces = relationship("AgentTrace", back_populates="interaction", cascade="all, delete-orphan")

class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True)
    step_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    inputs = Column(JSONB, nullable=False)
    outputs = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=dt.now, nullable=False)
    thinking = Column(Boolean, nullable=False)
    interaction_id_fk = Column(Integer, ForeignKey("interactions.id"))

    interaction = relationship("Interaction", back_populates="agent_traces")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    # CHANGED: engine creation is lazy. Alembic can import Base/metadata without
    # needing DB env vars until it actually connects for migrations/autogenerate.
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=False,
            future=True,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _sessionmaker

@asynccontextmanager
async def session_context():
    # Used by application code that wants `async with session_context()`.
    async with get_sessionmaker()() as session:
        yield session


async def get_session():
    # FastAPI dependency form. Do not decorate this with @asynccontextmanager:
    # Depends(get_session) expects an async generator and handles cleanup itself.
    async with get_sessionmaker()() as session:
        yield session
