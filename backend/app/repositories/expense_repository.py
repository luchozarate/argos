from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate

class ExpenseRepository:
    def create(self, db: Session, expense_in: ExpenseCreate, workspace_id: int) -> Expense:
        db_expense = Expense(
            workspace_id=workspace_id,
            description=expense_in.description,
            category=expense_in.category,
            amount=expense_in.amount,
            expense_date=expense_in.expense_date,
            # getattr evita crasheos si el esquema llega a estar desactualizado
            fixed_service_id=getattr(expense_in, 'fixed_service_id', None) 
        )
        db.add(db_expense)
        db.commit()           # ¡EL COMANDO QUE FALTABA!
        db.refresh(db_expense) # ¡PARA RECUPERAR LA FECHA EXACTA!
        return db_expense