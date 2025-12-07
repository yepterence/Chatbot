from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_engine():
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASS", "")
    DB_NAME = os.getenv("POSTGRES_DB_NAME", "chatbot")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")

    URL_DATABASE = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(URL_DATABASE, echo=False)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
