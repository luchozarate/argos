import os  # <-- ¡AQUÍ ESTÁ EL IMPORT QUE FALTA!
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  # <-- IMPORTANTE PARA ENVIAR EL HTML
from sqlalchemy import text

# Importación de routers de las APIs
from app.api.auth_api import router as auth_router
from app.api.user_api import router as user_router
from app.api.expense_api import router as expense_router
from app.api.ai_api import router as ai_router

# Importación de la Base de datos y modelos (necesarios para el create_all)
from app.database.database import Base, engine
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.expense import Expense

# Inicialización de la aplicación FastAPI (Una sola vez)
app = FastAPI(
    title="ARGOS API",
    version="0.1.0",
    description="Asistente financiero inteligente",
)

# Generación automática de tablas si no existen en PostgreSQL
Base.metadata.create_all(bind=engine)

# Inclusión de rutas / endpoints estructurados
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(ai_router)

# Configuración y montaje de archivos estáticos para la Web App móvil
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- Endpoints de Sistema e Interfaz ---

# Ruta raíz: Sirve la Web App directo al entrar a http://tu-ip:8000/
@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Monitoreo del contenedor
@app.get("/health")
def health():
    return {
        "status": "ok",
    }

# Testeo rápido de conexión con la base de datos PostgreSQL
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