import json
import os
from datetime import date
from google import genai
from google.genai import types
from fastapi import HTTPException
from app.schemas.expense import ExpenseCreate

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env")
        # Inicialización estándar de la SDK de Google GenAI
        self.client = genai.Client(api_key=api_key)

    def parse_expense(self, user_text: str) -> ExpenseCreate:
        today_str = date.today().isoformat()
        
        # Categorías oficiales extraídas del punto 5 y 10 de tu Documento de Visión
        categorias_validas = [
            "Hogar", "Alquiler", "Expensas", "Servicios", "Supermercado", 
            "Combustible", "Colegio", "Seguros", "Internet", "Streaming", 
            "Comida", "Negocios", "Impuestos", "Otros"
        ]
        categorias_str = ", ".join(categorias_validas)
        
        prompt = f"""
        Sos ARGOS, el asistente analista financiero experto. Tu tarea es extraer la información de un gasto a partir del texto del usuario.
        Fecha de referencia (hoy): {today_str}

        Debes clasificar el gasto obligatoriamente en una de las siguientes categorías válidas: [{categorias_str}].
        Si el gasto no encaja del todo en ninguna, usa "Otros".

        Texto del usuario: "{user_text}"

        Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
        {{
            "description": "Nombre claro y conciso del producto o lugar (ej: Carnicería, Distribuidora, Factura de Luz)",
            "category": "La categoría idéntica elegida de la lista proporcionada",
            "amount": monto numérico puro (ej: 30000.00),
            "expense_date": "Fecha del gasto en formato YYYY-MM-DD"
        }}
        No agregues markdown ni texto explicativo, solo el objeto JSON crudo.
        """

        try:
            # Usamos 'gemini-2.0-flash' (o 'gemini-2.5-flash-2026' según corresponda hoy), que es el modelo veloz disponible
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            
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
                detail=f"Error en el motor analítico de ARGOS: {str(e)}"
            )