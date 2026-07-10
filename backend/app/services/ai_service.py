import json
import os
from datetime import date
from google import genai
from google.genai import types
from fastapi import HTTPException
from app.schemas.expense import ExpenseCreate

class AIService:
    def __init__(self):
        # Tomamos la API Key desde las variables de entorno (.env)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env")
        self.client = genai.Client(api_key=api_key)

    def parse_expense(self, user_text: str) -> ExpenseCreate:
        # Le damos contexto temporal a la IA para que calcule fechas relativas ("ayer", "hoy")
        today_str = date.today().isoformat()
        
        prompt = f"""
        Sos un asistente financiero experto. Tu tarea es extraer la información de un gasto a partir del texto del usuario.
        Fecha de referencia (hoy): {today_str}

        Texto del usuario: "{user_text}"

        Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
        {{
            "description": "Nombre claro del producto o lugar (ej: Carnicería, Supermercado, Luz)",
            "category": "Categoría lógica (ej: Comida, Servicios, Transporte, Ocio)",
            "amount": monto numérico (ej: 30000.00),
            "expense_date": "Fecha del gasto en formato YYYY-MM-DD"
        }}
        No agregues texto explicativo, solo el JSON.
        """

        try:
            # Usamos gemini-2.5-flash porque es ultra rápido, económico y excelente con JSON
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            
            # Limpiamos y cargamos el JSON devuelto por la IA
            data = json.loads(response.text.strip())
            
            return ExpenseCreate(
                description=data["description"],
                category=data["category"],
                amount=data["amount"],
                expense_date=data["expense_date"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=422, 
                detail=f"La IA no pudo procesar el gasto de forma correcta: {str(e)}"
            )