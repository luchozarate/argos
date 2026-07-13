import calendar
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.fixed_service import FixedService
from app.models.expense import Expense
from app.schemas.fixed_service import FixedServiceResponse, FixedServiceStatusResponse, FixedServiceCreate
from app.security.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/fixed-services",
    tags=["Fixed Services"],
)

@router.post("/", response_model=FixedServiceResponse)
def create_fixed_service(
    service_in: FixedServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo servicio fijo recurrente.
    """
    new_service = FixedService(**service_in.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/workspace/{workspace_id}/status", response_model=List[FixedServiceStatusResponse])
def get_fixed_services_status(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los servicios fijos del workspace indicando si ya fueron pagados en el mes calendario actual.
    """
    # 1. Traer todos los servicios fijos del catálogo
    services = db.query(FixedService).filter(FixedService.workspace_id == workspace_id).order_by(FixedService.due_day.asc()).all()
    
    # 2. Obtener rango de fechas para el mes en curso
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = date(today.year, today.month, last_day)
    
    # 3. Buscar los gastos del mes que estén asociados a un servicio fijo
    month_expenses = db.query(Expense).filter(
        Expense.workspace_id == workspace_id,
        Expense.expense_date >= start_of_month,
        Expense.expense_date <= end_of_month,
        Expense.fixed_service_id.isnot(None)
    ).all()
    
    # Mapeo id_servicio_fijo -> gasto_realizado
    paid_mapping = {e.fixed_service_id: e for e in month_expenses}
    
    # 4. Consolidar el checklist de control de vencimientos
    result = []
    for s in services:
        expense_match = paid_mapping.get(s.id)
        result.append({
            "id": s.id,
            "name": s.name,
            "due_day": s.due_day,
            "category": s.category,
            "default_amount": float(s.default_amount) if s.default_amount else 0.0,
            "is_paid": expense_match is not None,
            "paid_amount": float(expense_match.amount) if expense_match else None,
            "paid_date": expense_match.expense_date.isoformat() if expense_match else None
        })
        
    return result