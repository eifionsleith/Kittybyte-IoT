from fastapi import FastAPI
from database import init_db
from api.routes.user import user_router
from api.routes.auth import auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")

@app.on_event("startup")
def initalize_db():
    init_db()

@app.get("/")
def root():
    return {"message": "😸"}
