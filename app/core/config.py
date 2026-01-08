from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Central Server"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    MISTRAL_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()