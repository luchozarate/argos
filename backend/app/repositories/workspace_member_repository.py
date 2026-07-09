from sqlalchemy.orm import Session

from app.models.workspace_member import WorkspaceMember


class WorkspaceMemberRepository:

    def create(
        self,
        db: Session,
        workspace_id: int,
        user_id: int,
        role: str = "owner",
    ) -> WorkspaceMember:

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )

        db.add(member)

        return member