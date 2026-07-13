from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password

class AuthService:

    def __init__(self):
        self.repository = UserRepository()

    def login(
        self,
        db: Session,
        email: str,
        password: str,
    ):

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