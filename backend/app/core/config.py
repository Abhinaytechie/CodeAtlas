from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DSA Platform API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017" # Default to local if no env var
    DB_NAME: str = "roadmap_guide_db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI/Gemini
    AI_API_KEY: Optional[str] = None

    class Config:
        # env_file = ".env" 
        pass

settings = Settings()
