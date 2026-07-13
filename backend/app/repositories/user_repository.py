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
        """Crea el usuario mapeando los campos del frontend real."""
        db_user = User(
            name=user_data.name,       # .name mapea a 'full_name' gracias al alias del schema
            email=user_data.email,     # .email es el correo real enviado
            password=hashed_password   # Contraseña encriptada
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user