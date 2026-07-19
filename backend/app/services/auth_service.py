from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import verify_password, get_password_hash
from app.schemas.user import UserCreate

# Importamos los modelos para crear el perfil
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

class AuthService:
    def __init__(self):
        self.repository = UserRepository()

    def login(self, db: Session, email: str, password: str):
        user = self.repository.get_by_email(db=db, email=email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas",
            )
        
        token = create_access_token({"sub": user.email, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}

    def register_user(self, db: Session, user_data: UserCreate):
        # 1. Verificar si el email ya existe
        existing_user = self.repository.get_by_email(db=db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # 2. Encriptar contraseña y crear Usuario
        hashed_password = get_password_hash(user_data.password)
        
        # OJO: dependiento de cómo armaste tu UserCreate, usamos .name
        new_user = self.repository.create_user_model(
            name=user_data.name, 
            email=user_data.email, 
            password=hashed_password
        )
        db.add(new_user)
        db.flush() # Guardamos temporalmente para obtener el ID del usuario

        # 3. AUTO-CREAR EL WORKSPACE (PERFIL) DEL USUARIO
        new_workspace = Workspace(name=f"Personal de {new_user.name}")
        db.add(new_workspace)
        db.flush() # Guardamos para obtener el ID del workspace

        # 4. VINCULAR AL USUARIO COMO DUEÑO DE ESE WORKSPACE
        new_member = WorkspaceMember(
            workspace_id=new_workspace.id, 
            user_id=new_user.id, 
            role="admin"
        )
        db.add(new_member)
        
        # 5. Confirmar todos los cambios en la Base de Datos
        db.commit()
        db.refresh(new_user)

        return {"message": "Usuario y Workspace creados con éxito", "user_id": new_user.id}