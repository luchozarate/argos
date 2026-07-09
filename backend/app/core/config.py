from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "ARGOS"

    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()