from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DSA Platform API"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017" # Default to local if no env var
    MONGO_PASSWORD: Optional[str] = None
    DB_NAME: str = "roadmap_guide_db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI/Gemini
    AI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.MONGO_PASSWORD and "<db_password>" in self.MONGO_URI:
            self.MONGO_URI = self.MONGO_URI.replace("<db_password>", self.MONGO_PASSWORD)
            
    from pydantic import field_validator
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

settings = Settings()
