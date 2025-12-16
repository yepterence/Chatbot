from sqlalchemy import create_engine, engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
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

    url_database = URL.create("postgresql+psycopg2", db_user, db_pass, db_host, db_port, db_name)

    config = {
        "sqlalchemy.url": url_database,
        "sqlalchemy.echo": False,
        "sqlalchemy.future": True,
    }
    return engine_from_config(config, prefix="sqlalchemy.")

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
