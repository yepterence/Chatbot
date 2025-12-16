from .session import SessionLocal
from .models import ChatHistory, ChatMessage

def create_chat_session(title: str):
    db = SessionLocal()
    session = ChatHistory(chat_title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    db.close()
    return session


def add_message(chat_id: int, role: str, content: str, datetime: str=None):
    db = SessionLocal()
    msg = ChatMessage(
        role=role,
        content=content,
        created_at=datetime,
        chat_history_id=chat_id
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()
    return msg
