from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_dsn: str = "postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry"


settings = Settings()
