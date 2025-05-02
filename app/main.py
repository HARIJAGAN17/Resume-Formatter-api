from fastapi import FastAPI
from app.routes.auth_route import router as auth_route
from app.database.db import Base, engine
from app.model import user_auth
from fastapi.middleware.cors import CORSMiddleware
from app.routes.resume_route import router as resume_route

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_route)
app.include_router(resume_route)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"welcome to resume formatter"}
