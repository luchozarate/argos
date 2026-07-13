import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# Database, Base and Engine
from app.database.database import Base, engine, get_db

# Models import (Crucial for SQLAlchemy table creation)
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.expense import Expense
from app.models.fixed_service import FixedService  # Nuevo modelo integrado

# Routers
from app.api.user_api import router as user_router
from app.api.auth_api import router as auth_router
from app.api.expense_api import router as expense_router
from app.api.ai_api import router as ai_router
from app.api.fixed_service_api import router as fixed_service_router  # Nuevo router integrado

app = FastAPI(
    title="ARGOS API",
    version="0.2.0",
    description="Asistente financiero inteligente y proactivo",
)

# Configuración de CORS para desarrollo y pruebas remotas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generación automática de tablas en PostgreSQL
Base.metadata.create_all(bind=engine)

# --- SISTEMA DE SEEDING AUTOMÁTICO DE SERVICIOS FIJOS ---
def seed_fixed_services():
    """
    Inicializa los servicios fijos del MVP por defecto si la tabla está vacía,
    para que Lucho tenga Luz, Gas, Alquiler, Expensas, Internet y Netflix listos para usar.
    """
    db: Session = next(get_db())
    try:
        count = db.query(FixedService).count()
        if count == 0:
            print("🌱 Base de datos vacía de servicios fijos. Inicializando catálogo por defecto...")
            default_services = [
                FixedService(name="Alquiler", due_day=5, category="Alquiler", default_amount=350000.00, workspace_id=1),
                FixedService(name="Expensas", due_day=10, category="Expensas", default_amount=55000.00, workspace_id=1),
                FixedService(name="Factura de Luz", due_day=12, category="Servicios", default_amount=28000.00, workspace_id=1),
                FixedService(name="Factura de Gas", due_day=15, category="Servicios", default_amount=12000.00, workspace_id=1),
                FixedService(name="Internet Wifi", due_day=18, category="Internet", default_amount=18000.00, workspace_id=1),
                FixedService(name="Suscripciones (Streaming)", due_day=20, category="Streaming", default_amount=7500.00, workspace_id=1),
            ]
            db.add_all(default_services)
            db.commit()
            print("✅ Catálogo inicializado con éxito.")
    except Exception as e:
        print(f"⚠️ Error al inicializar servicios fijos: {str(e)}")
    finally:
        db.close()

# Ejecutamos el Seeding automático al iniciar la aplicación
seed_fixed_services()

# Inclusión de Routers de FastAPI
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(ai_router)
app.include_router(fixed_service_router)  # Registrar el endpoint de fijos

# Configuración y montaje del frontend estático
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        version = connection.execute(text("SELECT version();")).scalar()
    return {
        "database": "connected",
        "version": version,
    }