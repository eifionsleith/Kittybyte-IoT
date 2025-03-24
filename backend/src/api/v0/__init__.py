from api.v0.routes.auth import router as auth_router
from api.v0.routes.device import router as device_router
from api.v0.routes.user import router as user_router

__all__ = [
        "auth_router",
        "device_router",
        "user_router"
        ]
