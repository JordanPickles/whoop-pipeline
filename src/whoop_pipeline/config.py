from pydantic_settings import BaseSettings
from pathlib import Path
import os
import json

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
TOKENS_JSON_PATH = Path(__file__).resolve().parents[2] / "tokens.json"

class Settings(BaseSettings):
    whoop_client_id: str
    whoop_client_secret: str
    whoop_api_base_url: str
    db_url: str
    whoop_refresh_token: str
    whoop_access_token: str
    whoop_redirect_uri: str
    whoop_auth_url: str
    whoop_token_url: str
    whoop_scope: str
    whoop_api_cycles_base_url: str
    whoop_access_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_refresh_token(self) -> str:
        refresh_token = self.whoop_refresh_token
        if refresh_token:
            return refresh_token
        elif TOKENS_JSON_PATH.exists():
            data = json.loads(TOKENS_JSON_PATH.read_text())
            refresh_token = data.get("refresh_token") 
            if refresh_token:
                return refresh_token
        raise RuntimeError("No refresh token found in env or .secrets/tokens.json")

settings = Settings()
