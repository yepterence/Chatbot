from sqlalchemy import create_engine

from api.config import Settings
from .models import Base
import os
from dotenv import load_dotenv

load_dotenv()
settings = Settings()

def init_db():
    DB_USER = settings.db_user
    DB_PASS = settings.db_pass
    DB_NAME = settings.db_name
    DB_HOST = settings.db_host
    DB_PORT = settings.db_port

    URL_DATABASE = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(URL_DATABASE)

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")