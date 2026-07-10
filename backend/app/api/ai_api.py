from fastapi import APIRouter, Depends
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
    # 1. La IA interpreta el texto plano y lo transforma en un objeto estructurado
    parsed_expense = ai_service.parse_expense(input_data.text)
    
    # 2. El servicio de gastos lo persiste en la base de datos PostgreSQL
    saved_expense = expense_service.create_expense(
        db=db, 
        expense_in=parsed_expense, 
        workspace_id=workspace_id
    )
    
    return saved_expense