#!/usr/bin/python3

from datetime import datetime as dt
import pytest
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from api.config import Settings
from db.models import ChatMessage
from db.schema_setup import init_db
from db.session import get_engine
load_dotenv()

TEST_DB_HOST = None
TEST_DB_PORT = None
TEST_DB_NAME = os.getenv("TEST_DB_NAME")
TEST_DB_PASS = os.getenv("TEST_DB_PASS")
TEST_DB_USER = os.getenv("TEST_DB_USER")

@pytest.fixture(scope="session")
def test_engine():
    engine = get_engine(TEST_DB_USER, TEST_DB_PASS, TEST_DB_HOST, TEST_DB_PORT, TEST_DB_NAME)
    return engine

@pytest.fixture
def db_session(test_engine):
    init_db(test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.rollback()
    db_session.close()

def test_add_message(db_session):
    current_time = dt.now().strftime("%m/%d/%Y, %H:%M:%S")
    msg = ChatMessage(role="user", content="hello", created_at=current_time)
    db_session.add(msg)
    db_session.commit()

    result = db_session.query(ChatMessage).first()
    assert isinstance(result.content, str)
    assert isinstance(result.role, str)
    assert isinstance(result.created_at, str)
    assert result.content == "hello"
