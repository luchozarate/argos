from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.ai import TextInput
from app.schemas.expense import ExpenseResponse
from app.services.ai_service import AIService
from app.services.expense_service import ExpenseService
from app.security.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
)

ai_service = AIService()
expense_service = ExpenseService()

@router.post("/process-text", response_model=ExpenseResponse)
def process_financial_text(
    input_data: TextInput,
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Procesa un texto libre, extrae el gasto mediante IA y lo registra en el Workspace.
    """
    parsed_expense = ai_service.parse_expense(input_data.text)
    saved_expense = expense_service.create_expense(
        db=db, 
        expense_in=parsed_expense, 
        workspace_id=workspace_id
    )
    return saved_expense

@router.post("/chat")
def chat_with_jarvis(
    input_data: TextInput,
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint conversacional interactivo con Jarvis (ARGOS) usando el historial real de gastos.
    """
    expenses = expense_service.get_workspace_expenses(db=db, workspace_id=workspace_id)
    income_test = 890000.0  # Sueldo neto estático de testeo
    
    reply = ai_service.generate_chat_response(
        user_message=input_data.text, 
        expenses=expenses, 
        income=income_test
    )
    return {"reply": reply}