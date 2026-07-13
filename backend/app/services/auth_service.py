from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password, get_password_hash
from app.schemas.user import UserCreate

class AuthService:

    def __init__(self):
        self.repository = UserRepository()

    def register_user(self, db: Session, user_data: UserCreate):
        """Lógica de negocio usando los tres campos reales."""
        # Validamos contra el email real del formulario
        existing_user = self.repository.get_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya está registrado"
            )
        
        hashed_password = get_password_hash(user_data.password)
        return self.repository.create(db, user_data=user_data, hashed_password=hashed_password)

    def login(self, db: Session, email: str, password: str):
        user = self.repository.authenticate(db=db, email=email)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": user.email, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}