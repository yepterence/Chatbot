from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from api.config import Settings

load_dotenv()
settings = Settings()

def get_engine(user=None, psw=None, host=None, port=None, db_name=None):
    db_user = user or settings.db_user
    db_pass = psw or settings.db_pass
    db_name = db_name or settings.db_name
    db_host = host or settings.db_host
    db_port = port or settings.db_port

    url_database = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url_database, echo=False)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
