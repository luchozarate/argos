from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def get_by_email(self, db: Session, email: str):
        """Busca un usuario por su email para verificar si ya existe."""
        return db.query(User).filter(User.email == email).first()

    def authenticate(self, db: Session, email: str):
        """Mantiene el método original que usa tu sistema de Login."""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_data: UserCreate, hashed_password: str):
        """Crea y persiste un nuevo usuario en la base de datos."""
        db_user = User(
            email=user_data.username,  # Mapeamos el 'username' del formulario al campo 'email'
            password=hashed_password   # Guardamos la contraseña ya encriptada
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user