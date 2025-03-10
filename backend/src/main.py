from fastapi import FastAPI
from database import init_db
from routes.auth import auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

@app.on_event("startup")
def initalize_db():
    init_db()

@app.get("/")
def root():
    return {"message": "😸"}
