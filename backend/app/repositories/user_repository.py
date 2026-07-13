from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def get_by_email(self, db: Session, email: str):
        """Busca un usuario por su email real."""
        return db.query(User).filter(User.email == email).first()

    def authenticate(self, db: Session, email: str):
        """Mantiene el método original para el Login."""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_data: UserCreate, hashed_password: str):
        """Crea el usuario usando los datos reales del frontend."""
        db_user = User(
            name=user_data.username,  # Guardamos el "usuario" real en 'name'
            email=user_data.email,     # Guardamos el "mail" real en 'email'
            password=hashed_password   # Contraseña encriptada
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user