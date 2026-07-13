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
        # Extraemos la parte anterior al '@' del correo y la hacemos Mayúscula inicial
        friendly_name = user_data.username.split('@')[0].capitalize()

        db_user = User(
            name=friendly_name,        # <--- ¡ESTA ES LA COLUMNA QUE POSTGRES EXIGÍA!
            email=user_data.username,  # Mapeamos el 'username' al campo 'email'
            password=hashed_password   # Guardamos la contraseña encriptada
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user