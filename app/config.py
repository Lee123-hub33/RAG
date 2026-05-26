import urllib.parse
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 1. Define individual database pieces with default fallbacks
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Lee@2026"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "compliance_mvp"

    # 2. Let Pydantic build the encoded URL dynamically
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Pydantic v2 modern configuration style
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()