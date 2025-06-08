from fastapi import FastAPI
from app.routes.auth_route import router as auth_route
from app.database.db import Base, engine
from app.model import user_auth
from fastapi.middleware.cors import CORSMiddleware
from app.routes.resume_route import router as resume_route
from app.routes.project_route import router as project_route
from app.routes.parsed_History import router as details_route
from app.routes.job_description_route import router as job_description_route
from app.routes.upload_file_route import router as upload_file_route

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
app.include_router(project_route)
app.include_router(details_route)
app.include_router(job_description_route)
app.include_router(upload_file_route)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"welcome to resume formatter"}
