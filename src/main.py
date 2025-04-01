from fastapi import FastAPI
from src.database import init_db
from src import links, auth
from src.projects import router as projects_router

app = FastAPI()


@app.on_event("startup")
def startup_event():

    init_db()


app.include_router(links.router)
app.include_router(auth.router)
app.include_router(projects_router)


@app.get("/")
def read_root():
    return {"message": "URL Shortener Service"}
