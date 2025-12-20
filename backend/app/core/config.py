from pydantic_settings import BaseSettings
from typing import Optional, List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "DSA Platform API"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000","https://yourcodeatlas.vercel.app"]
    
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
    
        self.MONGO_URI = self.MONGO_URI
            
    from pydantic import field_validator
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
             # Handle list-like string [url1, url2] or ['url1', 'url2']
            cleaned = v.strip("[]")
            return [i.strip().strip("'\"") for i in cleaned.split(",")]
        return v

settings = Settings()
