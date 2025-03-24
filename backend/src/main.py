from fastapi import FastAPI
from api.v0 import auth_router, device_router, user_router

from utils.database import Database
from utils.settings import get_settings

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(device_router, prefix="/device")
app.include_router(user_router, prefix="/user")

@app.on_event("startup")
def inititalize_db():
    settings = get_settings()
    database = Database(settings.database_url, echo=settings.database_echo_all)
    database.initialize_database()

@app.get("/")
def index():
    return {"message": "😸"}
