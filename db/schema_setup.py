from sqlalchemy import create_engine
from .models import Base
import os

def init_db():
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASS", "")
    DB_NAME = os.getenv("POSTGRES_DB_NAME", "chatbot")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")

    URL_DATABASE = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(URL_DATABASE)

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")