from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import UserCreate
from app.security.auth import get_current_user
from app.services.user_service import UserService
from app.models.user import User
from app.models.workspace_member import WorkspaceMember

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

service = UserService()

@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    created = service.create_user(
        db=db,
        name=user.name,
        email=user.email,
        password=user.password,
    )
    return {
        "id": created.id,
        "name": created.name,
        "email": created.email,
    }

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }

# --- NUEVO ENDPOINT PARA AISLAR LOS DATOS ---
@router.get("/me/workspaces")
def get_my_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve el ID del workspace privado del usuario logueado"""
    membership = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="No tienes ningún Workspace asignado")
        
    return {"workspace_id": membership.workspace_id}