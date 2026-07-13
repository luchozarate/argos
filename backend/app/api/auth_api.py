from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext

# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def login(self, db: Session, email: str, password: str):
        # Lógica existente de login...
        pass

    def register_user(self, db: Session, user: UserCreate):
        """
        Registra un nuevo usuario en la base de datos.
        """
        # 1. Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # 2. Hashear la contraseña
        hashed_password = pwd_context.hash(user.password)

        # 3. Crear el objeto usuario
        new_user = User(
            email=user.email,
            password=hashed_password,
            # Añade otros campos según tu modelo
        )

        # 4. Guardar en BD
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Usuario registrado con éxito", "user_id": new_user.id}