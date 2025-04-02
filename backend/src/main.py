from fastapi import FastAPI
import models
from utils.config import get_config
from api.routes.auth import router as auth_router
from api.routes.device import router as device_router
from utils.database import Database

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """
    Initiaizes the config object and the database tables.
    """
    app.state.config = get_config()
    Database(app.state.config.db_uri, echo=app.state.config.db_echo_all).initialize_database()

@app.get("/")
def default_route():
    return {"message": "😼"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(device_router, prefix="/device", tags=["device"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

