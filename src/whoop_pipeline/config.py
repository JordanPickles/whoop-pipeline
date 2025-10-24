from pydantic_settings import BaseSettings
from pathlib import Path
import os
import json
from typing import Optional

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
TOKENS_JSON_PATH = Path(__file__).resolve().parents[2] / ".secrets/tokens.json"

class Settings(BaseSettings):
    whoop_client_id: str
    whoop_client_secret: str
    whoop_api_base_url: str
    db_url: str
    whoop_refresh_token: Optional[str] = None
    whoop_redirect_uri: str
    whoop_auth_url: str
    whoop_token_url: str
    whoop_scope: str
    whoop_api_cycles_base_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    

settings = Settings()
if __name__ == "__main__":
    settings = Settings()
    print(settings.model_dump())
