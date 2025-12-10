from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from api.config import Settings

load_dotenv()
settings = Settings()

def get_engine():
    DB_USER = settings.db_user
    DB_PASS = settings.db_pass
    DB_NAME = settings.db_name
    DB_HOST = settings.db_host
    DB_PORT = settings.db_port

    URL_DATABASE = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(URL_DATABASE, echo=False)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
