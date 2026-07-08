from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


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
        return self.repository.create(
            db=db,
            name=name,
            email=email,
            password=password,
        )