import json
import os
import re
from datetime import date
from google import genai
from google.genai import types
from app.schemas.expense import ExpenseCreate

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        # Permitir que el backend inicie incluso sin API KEY
        if not api_key:
            print("⚠️ ADVERTENCIA: GEMINI_API_KEY no encontrada en .env. El modo offline será activado.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        
        # Leemos el modelo del .env o usamos el 3.5-flash por defecto que ya te funcionó
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    def parse_expense(self, text: str) -> ExpenseCreate:
        # 1. Instrucciones para la IA (con expense_date exigido)
        prompt = f"""
        Analiza el siguiente texto y extrae los detalles del gasto.
        Devuelve un JSON estrictamente con las siguientes claves:
        - description (str): Breve descripción del gasto.
        - category (str): Categoría (Supermercado, Alquiler, Servicios, Transporte, Comida, Entretenimiento, Otros).
        - amount (float): Monto total numérico.
        - expense_date (str): Fecha en formato YYYY-MM-DD. Hoy es {date.today().isoformat()}.
        - fixed_service_id (int o null): Si el gasto es claramente el pago de un servicio fijo (ej. luz, agua, alquiler), devuelve el ID numérico. Si no, devuelve null.

        Texto del usuario: "{text}"
        """
        
        # 2. Intento de conexión con Gemini
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                data = json.loads(response.text.strip())
                
                # Parche antibalas por si Gemini devuelve 'date' en lugar de 'expense_date'
                if "date" in data and "expense_date" not in data:
                    data["expense_date"] = data.pop("date")
                
                # Diagnostic flag si se usa IA real
                desc_real = f"{data['description']} 🤖"
                
                return ExpenseCreate(
                    description=desc_real,
                    category=data["category"],
                    amount=float(data["amount"]),
                    expense_date=data["expense_date"],
                    fixed_service_id=data.get("fixed_service_id")
                )
            except Exception as e:
                print(f"❌ DETALLE DE ERROR EN CHAT GEMINI: {str(e)}")
                print("⚠️ Activando failover analítico local comparativo...")
        
        # 3. Fallback (Jarvis de emergencia Offline)
        amount_match = re.search(r'\d+', text.replace('.', '').replace(',', ''))
        amount = float(amount_match.group()) if amount_match else 0.0
        
        category = "Otros"
        fixed_service_id = None
        
        text_lower = text.lower()
        if "luz" in text_lower or "edenor" in text_lower or "edesur" in text_lower:
            category = "Servicios"
            fixed_service_id = 3
        elif "alquiler" in text_lower:
            category = "Alquiler"
            fixed_service_id = 1
        elif "carniceria" in text_lower or "super" in text_lower or "comida" in text_lower:
            category = "Supermercado"
        
        desc_offline = f"{text[:30]}... 💻"
        
        # ¡Corregido! Acá usa expense_date=date.today()
        return ExpenseCreate(
            description=desc_offline,
            category=category,
            amount=amount,
            expense_date=date.today(),
            fixed_service_id=fixed_service_id
        )

    def generate_insights(self, expenses: list, income: float):
        prompt = f"""
        Actúa como Jarvis, un asistente financiero experto. 
        Aquí tienes los gastos del usuario este mes: {expenses}. Su ingreso base simulado es {income}.
        Devuelve un JSON con una lista llamada 'insights', donde cada elemento tenga:
        - type: "warning" (alerta), "advice" (consejo), "success" (buena noticia).
        - message: Un mensaje corto, humano y directo sobre cómo viene su economía.
        """
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                data = json.loads(response.text.strip())
                return data["insights"]
                
            except Exception as e:
                print(f"❌ Error al conectar con Gemini para insights: {str(e)}")
        
        # Fallback offline para insights
        return [
            {"type": "advice", "message": "💻 [Jarvis Offline] El motor cognitivo no pudo conectar. Revisa tus gastos manualmente por ahora."}
        ]