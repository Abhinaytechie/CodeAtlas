
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union

class Settings(BaseSettings):
    # Change type hint to allow string input, bypassing strict JSON parse
    BACKEND_CORS_ORIGINS: Union[List[str], str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, Union[str, List[str]]):
            if isinstance(v, str) and not v.startswith("["):
                print(f"Parsing string: {v}")
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
        raise ValueError(v)

# Test case 1: Comma separated string
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:5173,https://myapp.vercel.app"

try:
    print("Attempting to load settings with comma-separated string (Union type)...")
    settings = Settings()
    print(f"Success: Type: {type(settings.BACKEND_CORS_ORIGINS)} Value: {settings.BACKEND_CORS_ORIGINS}")
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
except Exception as e:
    print(f"Failed: {e}")
