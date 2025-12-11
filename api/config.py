from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Chatbot API"
    admin_email: str = "admin@email.com"
    items_per_user: int = 50
    db_user: str = os.getenv("DB_USER", "postgres")
    db_pass: str = os.getenv("DB_PASS", "")
    db_name: str = os.getenv("DB_NAME", "chatbot")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = os.getenv("DB_PORT", 5432)
