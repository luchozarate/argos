from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository

from app.security.password import hash_password


class UserService:

    def __init__(self):
        self.repository = UserRepository()
        self.workspace_repository = WorkspaceRepository()
        self.workspace_member_repository = WorkspaceMemberRepository()

    def create_user(
        self,
        db: Session,
        name: str,
        email: str,
        password: str,
    ):

        existing = self.repository.get_by_email(
            db=db,
            email=email,
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least 8 characters",
            )

        user = self.repository.create(
            db=db,
            name=name,
            email=email,
            password=hash_password(password),
        )

        db.flush()

        workspace = self.workspace_repository.create(
            db=db,
            name="Personal",
            owner_id=user.id,
        )

        self.workspace_member_repository.create(
            db=db,
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )

        db.commit()

        db.refresh(user)

        return user