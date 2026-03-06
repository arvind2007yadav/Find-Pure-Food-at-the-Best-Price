from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "food_profiler"
    crawl_interval_hours: int = 24
    max_concurrent_crawls: int = 5
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
