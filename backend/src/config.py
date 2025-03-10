from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expiry_minutes: int = 15
    database_url: str
    database_echo_all: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Config()   # TODO: Error Handling For Missing Configuration

