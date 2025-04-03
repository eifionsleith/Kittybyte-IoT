from utils.thingsboard import ThingsboardClient, ThingsboardAPIError
from utils.config import get_config
import pytest

config = get_config(env_file=".env.dev")

def test_login_successful():
    thingsboard_client = ThingsboardClient(
            config.thingsboard_hostname,
            username=config.thingsboard_username,
            password=config.thingsboard_password)
    thingsboard_client._login()

    print(f"token: {thingsboard_client._jwt_token}, refresh_token: {thingsboard_client._refresh_token}")
    assert thingsboard_client._jwt_token is not None

def test_login_invalid_credentials():
    incorrect_username = "INCORRECT"
    incorrect_password = "INCORRECT"
    thingsboard_client = ThingsboardClient(
            config.thingsboard_hostname,
            username=incorrect_username,
            password=incorrect_password)
    
    with pytest.raises(ThingsboardAPIError):
        thingsboard_client._login()

def test_login_missing_credentials():
    ##! Missing Password
    thingsboard_client = ThingsboardClient(
            config.thingsboard_hostname,
            username=config.thingsboard_username)
    with pytest.raises(ThingsboardAPIError):
        thingsboard_client._login()

    ##! Missing Username
    thingsboard_client = ThingsboardClient(
            config.thingsboard_hostname,
            password=config.thingsboard_password)
    with pytest.raises(ThingsboardAPIError):
        thingsboard_client._login()

    ##! Both Missing
    thingsboard_client = ThingsboardClient(
            config.thingsboard_hostname)

