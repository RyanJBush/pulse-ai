from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Pulse AI API"
    APP_VERSION: str = "0.2.0"
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://pulse:pulse@db:5432/pulse"
    LOG_LEVEL: str = "INFO"
    ANOMALY_THRESHOLD: float = 0.75
    ALERT_COOLDOWN_SECONDS: int = 300
    DEFAULT_REPLAY_COUNT: int = 120
    REPLAY_SPIKE_MULTIPLIER: float = 4.5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
