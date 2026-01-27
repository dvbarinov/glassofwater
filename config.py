from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    db_path: str = "data/aquatrack.db"

    class Config:
        env_file = ".env"