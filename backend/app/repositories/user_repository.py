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
        
    def get_by_email(
    self,
    db: Session,
    email: str,
):

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )