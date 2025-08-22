from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    whoop_client_id: str = Field(..., env="WHOOP_CLIENT_ID")
    whoop_client_secret: str = Field(..., env="WHOOP_CLIENT_SECRET")
    whoop_redirect_uri: AnyHttpUrl = Field(..., env="WHOOP_REDIRECT_URI")
    whoop_auth_url: AnyHttpUrl = Field(..., env="WHOOP_AUTH_URL")
    whoop_token_url: AnyHttpUrl = Field(..., env="WHOOP_TOKEN_URL")
    db_url: str = Field(..., env="DB_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


WHOOP_SCOPES = "read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement"