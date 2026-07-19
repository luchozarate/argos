from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password, get_password_hash
from app.schemas.user import UserCreate

# Modelos necesarios para crear el espacio privado del usuario
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

class AuthService:
    def __init__(self):
        self.repository = UserRepository()

    def login(self, db: Session, email: str, password: str):
        user = self.repository.authenticate(db=db, email=email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas",
            )
        
        token = create_access_token({"sub": user.email, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}

    def register_user(self, db: Session, user_data: UserCreate):
        # 1. Verificar si el usuario ya existe
        existing_user = self.repository.get_by_email(db=db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # 2. Hashear la contraseña y guardar al usuario
        hashed_password = get_password_hash(user_data.password)
        new_user = self.repository.create(db=db, user_in=user_data, hashed_password=hashed_password)

        # 3. AUTO-CREAR EL WORKSPACE (PERFIL PRIVADO) DEL USUARIO
        new_workspace = Workspace(name=f"Personal de {new_user.name}", owner_id=new_user.id)
        db.add(new_workspace)
        db.flush() # Guardamos temporalmente para obtener el workspace.id

        # 4. Vincular al usuario como administrador de su espacio
        new_member = WorkspaceMember(
            workspace_id=new_workspace.id,
            user_id=new_user.id,
            role="admin"
        )
        db.add(new_member)
        db.commit()

        return {"message": "Usuario registrado con éxito", "user_id": new_user.id}