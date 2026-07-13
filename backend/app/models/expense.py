from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    workspace_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clave foránea opcional que conecta el gasto con un servicio fijo estandarizado
    fixed_service_id = Column(Integer, ForeignKey("fixed_services.id"), nullable=True)
    fixed_service = relationship("FixedService", back_populates="expenses")