from dotenv import load_dotenv

from api.config import Settings
from api import logger
from .models import Base

load_dotenv()

def init_db(engine):

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")