from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate  # Importamos el esquema del Paso 1
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

service = AuthService()

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return service.login(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

# --- NUEVO ENDPOINT PARA REGISTRAR ---
@router.post("/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Endpoint para registrar nuevos usuarios en ARGOS."""
    return service.register_user(db=db, user_data=user_data)