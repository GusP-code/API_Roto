from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "API Roto")
    #DEBUG: bool = True
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")

    class Config:
        case_sensitive = True

settings = Settings() 