from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "API Roto"
    #DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Configuración de la base de datos
    DATABASE_URL: str = "mongodb+srv://gustavomaparicio:admin3219$0@cluster0.dw8dn0c.mongodb.net/?retryWrites=true&w=majority"
    DATABASE_NAME: str = "kits_db"

    class Config:
        case_sensitive = True

settings = Settings() 