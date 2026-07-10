from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.api.auth_api import router as auth_router
from app.api.user_api import router as user_router
from app.api.expense_api import router as expense_router
from app.database.database import Base, engine
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.expense import Expense
from app.api.ai_api import router as ai_router


app = FastAPI(
    title="ARGOS API",
    version="0.1.0",
    description="Asistente financiero inteligente",
)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="ARGOS API", version="0.1.0")
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(ai_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return {
        "project": "ARGOS",
        "version": "0.1.0",
        "status": "healthy",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT version();")
        ).scalar()

    return {
        "database": "connected",
        "version": version,
    }

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))