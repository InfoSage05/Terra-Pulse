from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TerraPulse Backend"
    API_V1_STR: str = "/v1"
    API_KEY: str = "dev_secret_key" # Default for dev, override with env var
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres" # Fallback if missing
    
    class Config:
        env_file = ".env"

settings = Settings()
