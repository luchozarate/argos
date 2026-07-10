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
            expense_date=expense_in.expense_date
        )
        db.add(db_expense)
        db.flush()  # Para obtener el ID antes del commit definitivo
        return db_expense

    def get_by_workspace(self, db: Session, workspace_id: int, limit: int = 100):
        return db.query(Expense).filter(Expense.workspace_id == workspace_id).limit(limit).all()