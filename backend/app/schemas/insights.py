from pydantic import BaseModel
from typing import List

class FinancialInsight(BaseModel):
    type: str # "warning" (alerta), "advice" (consejo), "success" (buena noticia)
    message: str # El consejo directo de Jarvis

class InsightsResponse(BaseModel):
    insights: List[FinancialInsight]