from typing import Optional
from fastapi import HTTPException, status
from tb_rest_client.rest_client_ce import RestClientCE


class ThingsboardHandler:
    def __init__(self):
        self.client: Optional[RestClientCE] = None

    def initialize_and_login(self, base_url: str, username: str, password: str):
        if self.client is not None:
            return  # Already initialized - don't initialize again.

        self.client = RestClientCE(base_url=base_url)
        try:
            self.client.login(username, password)
            self.client.get_user()
            self.client.start()

        except Exception:
            self.client = None  # Login failed, so no client.
            raise

    def shutdown(self):
        if self.client and self.client.is_alive():
            self.client.stop()
            self.client = None

    def get_client(self) -> RestClientCE:
        if not self.client:
            raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Thingsboard Service Unavailable"
                    )
        return self.client

