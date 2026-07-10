from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate

class ExpenseService:
    def __init__(self):
        self.repository = ExpenseRepository()

    def create_expense(self, db: Session, expense_in: ExpenseCreate, workspace_id: int):
        # Acá se podrían meter reglas de negocio en el futuro
        expense = self.repository.create(db, expense_in, workspace_id)
        db.commit()
        return expense

    def get_workspace_expenses(self, db: Session, workspace_id: int):
        return self.repository.get_by_workspace(db, workspace_id)