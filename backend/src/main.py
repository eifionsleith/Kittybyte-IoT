from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.auth import router as auth_router
from src.api.routes.device import router as device_router
from src.api.routes.schedule import router as schedule_router
from src.api.routes.user import router as user_router
from src.utils.config import get_config
from src.utils.database import Database
from src.utils.thingsboard.thingsboard_handler import ThingsboardHandler


ENV_FILE = ".env.dev"
ENV_FILE_ENCODING = "utf-8"

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(device_router, prefix="/device", tags=["device"])
app.include_router(schedule_router, prefix="/schedule", tags=["schedule"])

@app.on_event("startup")
def startup_event():
    app.state.settings = get_config(ENV_FILE, ENV_FILE_ENCODING)
    app.state.thingsboard_handler = ThingsboardHandler(app.state.settings.thingsboard.host,
                                                       app.state.settings.thingsboard.username,
                                                       app.state.settings.thingsboard.password)
    Database(app.state.settings.db.uri, app.state.settings.db.echo_all)\
            .initialize_tables()

@app.get("/")
def default_route():
    return {"message": "😼"}

