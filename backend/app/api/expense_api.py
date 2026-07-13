from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.services.expense_service import ExpenseService
from app.security.auth import get_current_user
from app.models.user import User

# Importamos el esquema definido en el Canvas para la serialización
from app.schemas.expense_schema import expense_schema, expenses_schema

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)

service = ExpenseService()

@router.post("/")
def create_expense(
    expense_data: dict, # Recibe el JSON plano
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo gasto validado mediante el schema del Canvas.
    """
    # Validamos los datos usando el esquema de Marshmallow
    errors = expense_schema.validate(expense_data)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
        
    saved_expense = service.create_expense(db=db, expense_in=expense_data, workspace_id=workspace_id)
    return expense_schema.dump(saved_expense)

@router.get("/workspace/{workspace_id}")
def get_expenses(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los gastos de un workspace y los serializa con el esquema del Canvas.
    """
    expenses = service.get_workspace_expenses(db=db, workspace_id=workspace_id)
    return expenses_schema.dump(expenses)