from fastapi import APIRouter, Depends
from app.schemas.insights import InsightsResponse
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

# Inyectamos el nuevo endpoint abajo
@router.get("/insights", response_model=InsightsResponse)
def get_financial_insights(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Buscamos los gastos reales del usuario en la base de datos
    expenses = expense_service.get_workspace_expenses(db=db, workspace_id=workspace_id)
    
    # 2. Hardcodeamos el ingreso del punto 9 ($890.000) por ahora para el test
    income_test = 890000.0
    
    # 3. Mandamos los datos reales al motor de IA (con failover incluido)
    ai_insights = ai_service.generate_financial_insights(expenses, income_test)
    
    return {"insights": ai_insights}

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