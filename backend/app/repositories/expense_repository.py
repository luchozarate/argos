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
            fixed_service_id=expense_in.fixed_service_id  # ¡Agregado para que lo guarde en la BD!
        )
        db.add(db_expense)
        db.flush()  # Para obtener el ID antes del commit definitivo
        return db_expense