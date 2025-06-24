from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional
from pathlib import Path

# Obtener la ruta del directorio actual
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    APP_NAME: str = "API Roto"
    API_V1_STR: str = "/api/v2"
    
    # Configuración de la base de datos
    DATABASE_URL: Optional[str] = None
    DATABASE_NAME: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validar que las variables críticas estén presentes
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL no está configurada en las variables de entorno")
        if not self.DATABASE_NAME:
            raise ValueError("DATABASE_NAME no está configurada en las variables de entorno")

    class Config:
        env_file = str(env_path)
        case_sensitive = True

settings = Settings() 