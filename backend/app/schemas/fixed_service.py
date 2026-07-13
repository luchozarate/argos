from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class FixedServiceBase(BaseModel):
    name: str
    due_day: int
    category: str
    default_amount: Optional[Decimal] = None
    workspace_id: int

class FixedServiceCreate(FixedServiceBase):
    pass

class FixedServiceResponse(FixedServiceBase):
    id: int

    class Config:
        from_attributes = True

class FixedServiceStatusResponse(BaseModel):
    id: int
    name: str
    due_day: int
    category: str
    default_amount: float
    is_paid: bool
    paid_amount: Optional[float] = None
    paid_date: Optional[str] = None