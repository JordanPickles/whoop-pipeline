from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from pathlib import Path
import json
from pathlib import Path
from typing import Optional

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
TOKENS_JSON = Path(__file__).resolve().parents[2] / ".secrets" / "tokens.json"

class Settings(BaseSettings):
    whoop_client_id: str
    whoop_client_secret: str
    whoop_api_base_url: str
    db_url: str
    whoop_refresh_token: Optional[str] = None
    whoop_redirect_uri: Optional[str] = None
    whoop_auth_url: Optional[str] = None
    whoop_token_url: Optional[str] = None
    whoop_scope: Optional[str] = None
    whoop_api_cycles_base_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    
    # Simple helper: ENV first, then tokens.json (local) if not working with env vars
    def get_refresh_token(self) -> str:
        if self.whoop_refresh_token:
            return self.whoop_refresh_token
        if TOKENS_JSON.exists():
            with open(TOKENS_JSON, "r") as f:
                data = json.load(f)
            token = data.get("refresh_token")
            if token:
                return token
        raise RuntimeError(
            "No refresh token found. Set WHOOP_REFRESH_TOKEN in env/Secrets, "
            "or put .secrets/tokens.json with {'refresh_token':'...'}"
        )

settings = Settings()


    # whoop_client_id: str = Field(..., env="WHOOP_CLIENT_ID")
    # whoop_client_secret: str = Field(..., env="WHOOP_CLIENT_SECRET")
    # whoop_redirect_uri: AnyHttpUrl = Field(..., env="WHOOP_REDIRECT_URI")
    # whoop_auth_url: AnyHttpUrl = Field(..., env="WHOOP_AUTH_URL")
    # whoop_token_url: AnyHttpUrl = Field(..., env="WHOOP_TOKEN_URL")
    # whoop_scope: str = Field(..., env="WHOOP_SCOPE")
    # whoop_api_base_url: AnyHttpUrl = Field(..., env="WHOOP_API_BASE_URL")
    # whoop_api_cycles_base_url: AnyHttpUrl = Field(..., env="WHOOP_API_CYCLES_BASE_URL")
    # db_url: str = Field(..., env="DB_URL")
