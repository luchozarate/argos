from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user import UserCreate
from app.api.auth_service import AuthService # Asegúrate de importar tu servicio

# 1. Definimos el router (ESTO ES LO QUE LE FALTA A TU ARCHIVO)
router = APIRouter(prefix="/auth", tags=["auth"])

# Instancia del servicio
auth_service = AuthService()

# 2. Definimos las rutas que usan el servicio
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user)

# Aquí puedes añadir tu endpoint de login, etc.
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    return auth_service.login(db, email, password)