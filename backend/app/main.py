from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import Base, engine
from app.models.user import User
from sqlalchemy import text
from app.api.user_api import router as user_router

app = FastAPI(
    title="ARGOS API",
    version="0.1.0",
    description="Asistente financiero inteligente"
)
app.include_router(user_router)
Base.metadata.create_all(bind=engine)

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