from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from fastapi import HTTPException
from app.security.password import hash_password


class UserService:

    def __init__(self):
        self.repository = UserRepository()

    def create_user(
    self,
    db: Session,
    name: str,
    email: str,
    password: str,
):

    existing = self.repository.get_by_email(
        db=db,
        email=email,
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters",
        )

    user = self.repository.create(
        db=db,
        name=name,
        email=email,
        password=hash_password(password),
    )

    db.commit()
    db.refresh(user)

    return user