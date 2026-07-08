from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import engine

from app.database.database import engine
from sqlalchemy import text

app = FastAPI(
    title="ARGOS API",
    version="0.1.0",
    description="Asistente financiero inteligente"
)


@app.get("/")
def root():
    return {
        "project": "ARGOS",
        "version": "0.1.0",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        version = connection.execute(text("SELECT version();")).scalar()

    return {
        "database": "connected",
        "version": version
    }