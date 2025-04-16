from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    uri: str
    echo_all: bool = False

class JWTSettings(BaseModel):
    secret: str
    algorithm: str = "HS256"
    expiry_minutes: int = 90

class ThingsboardProvisioningSettings(BaseModel):
    key: str
    secret: str

class ThingsboardSettings(BaseModel):
    host: str
    username: str
    password: str
    provisioning: ThingsboardProvisioningSettings

class AppSettings(BaseSettings):
    db: DatabaseSettings
    jwt: JWTSettings
    thingsboard: ThingsboardSettings

    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            env_nested_delimiter="_",
            case_sensitive=False)

def get_config(env_file: str = ".env",
               env_file_encoding: str = "utf-8"):
    """
    Creates an instance of AppSettings using the provided .env file.
    This contains the environment variables needed to run the app.

    Args:
        env_file (str): Path to the environment variables file.
            Defaults to ".env"
        env_file_encoding (str): Environment variables file encoding format.
            Defaults to "utf-8"

    Returns:
        AppSettings: Initialized instance of AppSettings.
    """
    try: return AppSettings(_env_file=env_file, _env_file_encoding=env_file_encoding) # pyright: ignore[reportCallIssue]
    except ValidationError as e:
        raise SystemExit("Configuration error, cannot start application. Please review .env file.") from e
