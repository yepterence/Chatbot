from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Chatbot API"
    admin_email: str = "admin@email.com"
    items_per_user: int = 50
    # Database
    db_user: str
    db_pass: str
    db_name: str
    db_host: str
    db_port: int
    llm_backend: str = "local"
    llm_model: str = "gemma3"
    google_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
