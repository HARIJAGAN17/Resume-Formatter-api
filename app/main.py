from fastapi import FastAPI
from app.routes.auth_route import router as auth_route
from app.database.db import Base, engine
from app.model import user_auth

app = FastAPI()
app.include_router(auth_route)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"welcome to resume formatter"}
