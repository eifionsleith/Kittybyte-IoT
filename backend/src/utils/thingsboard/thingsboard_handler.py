from fastapi import HTTPException, status
from tb_rest_client.rest_client_ce import RestClientCE


class ThingsboardHandler:
    def __init__(self, base_url: str, username: str, password: str):
        self.client = RestClientCE(base_url=base_url)
        self.client.login(username, password)
        self.client.start()
    
    def get_client(self) -> RestClientCE:
        if not self.client.is_alive():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Thingsboard Service Unavailable")
        return self.client

