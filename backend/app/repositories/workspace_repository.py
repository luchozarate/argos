from sqlalchemy.orm import Session

from app.models.workspace import Workspace


class WorkspaceRepository:

    def create(
        self,
        db: Session,
        name: str,
        owner_id: int,
    ) -> Workspace:

        workspace = Workspace(
            name=name,
            owner_id=owner_id,
        )

        db.add(workspace)
        db.flush()

        return workspace