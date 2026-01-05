from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Chatbot API"
    admin_email: str = "admin@email.com"
    items_per_user: int = 50
    db_user: str
    db_pass: str
    db_name: str
    db_host: str
    db_port: int
