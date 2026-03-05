from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PriceIntel SaaS"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # DATABASE
    DATABASE_URL: str = "sqlite:///priceintel.db"
    
    # REDIS / CELERY
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # SCRAPING
    PROXY_URL: str | None = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
