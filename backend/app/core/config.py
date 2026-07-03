from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "TerraPulse Backend"
    API_V1_STR: str = "/v1"
    API_KEY: str = "dev_secret_key"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

settings = Settings()
