
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            print(f"Parsing string: {v}")
            return [i.strip() for i in v.split(",")]
        return v

# Test case 1: Comma separated string (What I told the user to do)
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:5173,https://myapp.vercel.app"

try:
    print("Attempting to load settings with comma-separated string...")
    settings = Settings()
    print(f"Success: {settings.BACKEND_CORS_ORIGINS}")
except Exception as e:
    print(f"Failed: {e}")

print("-" * 20)

# Test case 2: Invalid JSON (Single quotes - common user error)
os.environ["BACKEND_CORS_ORIGINS"] = "['http://localhost:5173']"

try:
    print("Attempting to load settings with single-quoted list (Invalid JSON)...")
    settings = Settings()
    print(f"Success: {settings.BACKEND_CORS_ORIGINS}")
except Exception as e:
    print(f"Failed: {e}")
