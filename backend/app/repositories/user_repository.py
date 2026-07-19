from sqlalchemy.orm import Session 
from app.models.user import User 
from app.schemas.user import UserCreate

class UserRepository: 
    def get_by_email(self, db: Session, email: str): 
        """Busca un usuario por su email real.""" 
        return db.query(User).filter(User.email == email).first()

    def create_user_model(self, name: str, email: str, password: str) -> User:
        """Instancia el modelo del usuario listo para ser guardado en la BD."""
        return User(
            name=name,
            email=email,
            password=password
        )