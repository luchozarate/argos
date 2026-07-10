from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from datetime import datetime

class ExpenseBase(BaseModel):
    description: str
    category: str
    amount: Decimal
    expense_date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    workspace_id: int
    created_at: datetime

    class Config:
        from_attributes = True