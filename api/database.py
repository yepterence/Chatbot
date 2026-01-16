#!/usr/bin/python3

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from api.config import Settings
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Integer, select
from sqlalchemy.orm import DeclarativeBase, relationship, selectinload
from datetime import datetime as dt

from api.logger import get_logger

logger = get_logger("db_setup")

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

settings = Settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:"
    f"{settings.db_pass}@{settings.db_host}:"
    f"{settings.db_port}/{settings.db_name}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def create_chat_session(title: str, session: AsyncSession) -> ChatHistory:
    chat_history_session = ChatHistory(chat_title=title)
    session.add(chat_history_session)
    await session.flush()
    await session.commit()
    return session

async def add_message(
    chat_id: int,
    role: str,
    content: str,
    session: AsyncSession,
    created_at: str,
) -> ChatMessage:
    msg = ChatMessage(
        role=role,
        content=content,
        created_at=created_at,
        chat_history_id_fk=chat_id,
    )
    session.add(msg)
    await session.flush()
    await session.commit()
    return msg

async def get_chat_messages(session: AsyncSession, chat_id: int):

    try:
        clean_chat_id = int(chat_id)
    except (ValueError, TypeError):
        return None
    async with session as db_session:
        stmt = select(ChatHistory).options(selectinload(ChatHistory.chat_messages)).where(ChatHistory.id == clean_chat_id)
        res = await db_session.execute(stmt)
        return res.scalar_one_or_none()

async def get_chat_history(session: AsyncSession):

    async with session as db_session:
        stmt = select(ChatHistory)
        res = await db_session.execute(stmt)
        return res.scalars().all()

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        raise Exception("Failed to initialize db with desired tables.")
    