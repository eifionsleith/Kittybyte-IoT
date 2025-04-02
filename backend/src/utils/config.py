from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 30

    db_uri: str
    db_echo_all: bool = False

    thingsboard_hostname: str
    thingsboard_provision_key: str
    thingsboard_provision_secret: str

    class Config:
        env_file: str = ".env.dev"
        env_file_encoding: str = "utf-8"

def get_config(
        env_file: str = ".env.dev", 
        env_file_encoding: str = "utf-8") -> AppConfig:
    """
    Gets the environment variables object using the provided
    input dotfile, this is mostly a workaround for LSPs.

    Args:
        env_file (str): Path to the environment variable file.
            Defaults to ".env"
        env_file_encoding (str): Optional encoding format, as str.
            Defaults to "utf-8"
    Returns:
        AppConfig: Object containing the environment variables.
    """
    return AppConfig(_env_file=env_file, _env_file_encoding=env_file_encoding) # pyright: ignore[reportCallIssue]

