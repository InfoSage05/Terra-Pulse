from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "TerraPulse Backend"
    API_V1_STR: str = "/v1"
    # Single static shared secret compared with `==` - fine as a pre-launch
    # placeholder, but it does NOT support per-client identity, scoping, or
    # audit trails. API_KEYS (plural, comma-separated) lets ops rotate a key
    # without downtime (add the new one, deploy, remove the old one) - this
    # is NOT a real auth/authz system and shouldn't be treated as one
    # elsewhere in the codebase.
    API_KEY: str = "dev_secret_key"
    API_KEYS: str = ""
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    REDIS_URL: str = "redis://localhost:6379/0"
    AREA_SCORE_CACHE_TTL_SECONDS: int = 3600
    # List endpoints (areas/, areas/summary, neighborhoods/, neighborhoods/featured)
    # change whenever ingestion runs, same as area scores, but are read far
    # more often (every homepage/map load) - shorter TTL than area scores
    # would be reasonable if this ever needs tuning independently, but for
    # now both are driven by the same underlying refresh cadence.
    AREA_LIST_CACHE_TTL_SECONDS: int = 900
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def valid_api_keys(self) -> set[str]:
        keys = {self.API_KEY} if self.API_KEY else set()
        keys.update(k.strip() for k in self.API_KEYS.split(",") if k.strip())
        return keys

settings = Settings()
