from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
from typing import Optional

class ExpenseBase(BaseModel):
    description: str
    category: str
    amount: Decimal
    expense_date: date
    fixed_service_id: Optional[int] = None  # ¡Agregado para que no se pierda el ID del fijo!

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    workspace_id: int
    created_at: datetime