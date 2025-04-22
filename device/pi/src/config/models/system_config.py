from typing import Optional
from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
    thingsboard_host: str = Field(default="thingsboard.cs.cf.ac.uk",
                                  description="Host for thingsboard, used as MQTT broker.")
    thingsboard_mqtt_port: int = Field(default=1883,
                                       description="Port used for Thingsboard MQTT communication.")
    thingsboard_token: Optional[str] = Field(default=None,
                                             description="Token used for Thingsboard communication, configured during provisioning.")

