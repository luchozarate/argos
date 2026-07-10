from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.expense_service import ExpenseService
from app.security.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)

service = ExpenseService()

@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense_in: ExpenseCreate,
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protegido con JWT
):
    # Nota: Idealmente verificar si el current_user pertenece a ese workspace_id
    return service.create_expense(db=db, expense_in=expense_in, workspace_id=workspace_id)

@router.get("/workspace/{workspace_id}", response_model=List[ExpenseResponse])
def get_expenses(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_workspace_expenses(db=db, workspace_id=workspace_id)