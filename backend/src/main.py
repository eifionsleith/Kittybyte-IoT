from fastapi import FastAPI

from api.routes.auth import router as auth_router
from api.routes.device import router as device_router
from utils.config import get_config
from utils.database import Database 
from utils.thingsboard.thingsboard_handler import ThingsboardHandler


app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(device_router, prefix="/device", tags=["device"])

#! TODO: Lifespan
@app.on_event("startup")
def startup_event():
    app.state.config = get_config(".env.dev")
    app.state.thingsboard_handler = ThingsboardHandler()
    app.state.thingsboard_handler.initialize_and_login(
            app.state.config.thingsboard.host,
            app.state.config.thingsboard.username,
            app.state.config.thingsboard.password
            )

    Database(app.state.config.db.uri, echo=app.state.config.db.echo_all).initalize_tables()

@app.get("/")
def default_route():
    return {"message": "😼"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

