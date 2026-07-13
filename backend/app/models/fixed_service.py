from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class FixedService(Base):
    __tablename__ = "fixed_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    due_day = Column(Integer, nullable=False)  # Día de vencimiento del mes (ej: 10)
    category = Column(String, nullable=False)  # e.g., "Servicios", "Alquiler", "Internet"
    default_amount = Column(Numeric(12, 2), nullable=True) # Monto esperado
    workspace_id = Column(Integer, nullable=False)

    # Relación uno-a-muchos con los gastos pagados reales
    expenses = relationship("Expense", back_populates="fixed_service")