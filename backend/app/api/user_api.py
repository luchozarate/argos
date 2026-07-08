from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
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