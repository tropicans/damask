import json
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SecureData Web"
    PORT: int = 8000
    CORS_ALLOWED_ORIGINS: str = '["http://localhost:5173"]'
    DATABASE_URL: str = "sqlite:///datamask.db"
    JWT_SECRET_KEY: str = "secret-key-for-dev-purposes-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    COOKIE_SECURE: bool = False

    @property
    def cors_origins(self) -> list[str]:
        try:
            return json.loads(self.CORS_ALLOWED_ORIGINS)
        except Exception:
            return ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

