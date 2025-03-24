from pydantic_settings import BaseSettings

# TODO: Support different dotfiles, e.g. .env and .env.dev without
#       needing to change the code, e.g. via param to main.

class AppSettings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str
    jwt_access_token_expiry_minutes: int = 15

    database_url: str
    database_echo_all: bool = False

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"

def get_settings() -> AppSettings:
    """
    Gets the environment variables object.
    This is mostly a workaround to make pydantic_settings work with Pyright(LSP).

    Returns:
        AppSettings: Class containing the environment variables for the app.
    """
    return AppSettings() # pyright: ignore[reportCallIssue]

