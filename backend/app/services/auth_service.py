from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password, get_password_hash  # Agregamos get_password_hash
from app.schemas.user import UserCreate  # Importamos el esquema del Paso 1

class AuthService:

    def __init__(self):
        self.repository = UserRepository()

    def register_user(self, db: Session, user_data: UserCreate):
        """Lógica de negocio para registrar un usuario de forma segura."""
        # 1. Verificar si el email ya existe usando el método que creamos en el repositorio
        existing_user = self.repository.get_by_email(db, email=user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya está registrado"
            )
        
        # 2. Hashear la contraseña de manera segura
        hashed_password = get_password_hash(user_data.password)
        
        # 3. Llamar al repositorio para guardar el nuevo registro en PostgreSQL
        return self.repository.create(db, user_data=user_data, hashed_password=hashed_password)

    def login(
        self,
        db: Session,
        email: str,
        password: str,
    ):
        # Este método se mantiene exactamente igual a tu versión original
        user = self.repository.authenticate(
            db=db,
            email=email,
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        token = create_access_token(
            {
                "sub": user.email,
                "user_id": user.id,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }