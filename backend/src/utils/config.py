from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    uri: str
    echo_all: bool = False

class JWTSettings(BaseModel):
    secret: str
    algorithm: str = "HS256"
    expiry_minutes: int = 30

class ProvisioningSettings(BaseModel):
    key: str
    secret: str

class ThingsboardSettings(BaseModel):
    host: str
    username: str
    password: str
    provisioning: ProvisioningSettings

class AppConfig(BaseSettings):
    db: DatabaseSettings
    jwt: JWTSettings
    thingsboard: ThingsboardSettings

    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            env_nested_delimiter="_",
            case_sensitive=False
    )

def get_config(env_file: str = ".env",
               env_file_encoding: str = "utf-8") -> AppConfig:
    """
    Creates an instance of AppConfig using the settings from the provided .env file.

    Improves LSP support.
    
    Args:
        env_file (str): Path to the dotenv environment variables file.
            Defaults to ".env"
        env_file_encoding (str): Optional encoding format.
            Defaults to "utf-8"

    Returns:
        AppConfig: Initialized instance of AppConfig.
    """
    try:
        return AppConfig(_env_file=env_file, _env_file_encoding=env_file_encoding) # pyright: ignore[reportCallIssue]
    except ValidationError as e:
        raise SystemExit("Configuration error, cannot start application. Please review .env file.") from e

