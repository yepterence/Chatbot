from dotenv import load_dotenv

from api.logger import get_logger
from .models import Base

load_dotenv()
logger = get_logger("db_setup")
def init_db(engine):

    logger.debug("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.debug("Done!")