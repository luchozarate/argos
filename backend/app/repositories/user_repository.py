from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def create(
        self,
        db: Session,
        name: str,
        email: str,
        password: str,
    ) -> User:

        user = User(
            name=name,
            email=email,
            password=password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user