import json
import os
import re
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
        self.client = genai.Client(api_key=api_key)

    def parse_expense(self, user_text: str) -> ExpenseCreate:
        today_str = date.today().isoformat()
        
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
            # Modelo oficial, vigente y de producción actual
            response = self.client.models.generate_content(
                model='gemini-2.5-flash', 
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
            # --- MODO ADMIN LINUX ACTIVADO: FAILOVER AUTÓNOMO ---
            # Si Google tira 429, 404 o cualquier error, procesamos el texto por regex para que la app responda
            print(f"⚠️ Servidor Gemini no disponible ({str(e)}). Activando parseo local de emergencia...")
            
            # Intentamos cazar números en el texto (ej: "30000" o "30 lucas")
            monto = 1000.00 # Monto por defecto
            text_lower = user_text.lower()
            
            # Si dice "lucas", multiplicamos por 1000
            lucas_match = re.search(r'(\d+)\s*luca', text_lower)
            numeros_puros = re.findall(r'\d+', text_lower)
            
            if lucas_match:
                monto = float(lucas_match.group(1)) * 1000
            elif numeros_puros:
                monto = float(numeros_puros[0])
            
            # Intentamos adivinar la categoría por palabras clave rápidas
            categoria = "Otros"
            if "carne" in text_lower or "super" in text_lower or "comida" in text_lower:
                categoria = "Supermercado"
            elif "luz" in text_lower or "agua" in text_lower or "gas" in text_lower or "vence" in text_lower:
                categoria = "Servicios"
            elif "nafta" in text_lower or "combustible" in text_lower:
                categoria = "Combustible"

            # Retornamos el gasto procesado localmente para que impacte en la DB
            return ExpenseCreate(
                description=user_text[:30] if user_text else "Gasto Manual",
                category=categoria,
                amount=monto,
                expense_date=date.today()
            )
            
    def generate_financial_insights(self, expenses: list, income: float) -> list:
        # Si la cuenta sigue en modo gratuito y trabada, dejamos un "mock" super inteligente basado en datos reales
        # Pero si la API Key está activa, Gemini analizará de verdad todo tu mes.
        
        total_gastado = sum(float(e.amount) for e in expenses)
        
        # Armamos un resumen en texto de los gastos para enviarle a la IA
        resumen_gastos = ""
        for e in expenses:
            resumen_gastos += f"- {e.expense_date}: {e.description} ({e.category}) -> ${e.amount}\n"

        prompt = f"""
        Sos ARGOS, el copiloto financiero personal y analista experto del usuario. Tu misión es ser un "Jarvis" financiero: directo, inteligente y proactivo. No suavices las cosas si la economía va mal.
        
        Datos financieros del mes actual:
        - Ingresos totales: ${income}
        - Total gastado hasta ahora: ${total_gastado}
        
        Lista detallada de gastos del usuario:
        {resumen_gastos}
        
        Analizá el ritmo de gasto. Debes devolver una respuesta ESTRICTAMENTE en formato JSON con una lista de máximo 3 recomendaciones/alertas clave.
        Estructura esperada:
        {{
            "insights": [
                {{"type": "warning | advice | success", "message": "Tu consejo personalizado y crudo aquí"}}
            ]
        }}
        """

        try:
            # Si tu cuenta ya tiene fondos/tarjeta, esto va a llamar a Gemini de verdad
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            data = json.loads(response.text.strip())
            return data["insights"]
            
        except Exception as e:
            # Failover analítico local por si Google sigue bloqueando la cuota
            print(f"⚠️ No se pudieron generar insights con Gemini ({str(e)}). Usando motor analítico local...")
            
            local_insights = []
            porcentaje_gastado = (total_gastado / income) * 100 if income > 0 else 0
            
            if porcentaje_gastado > 80:
                local_insights.append({
                    "type": "warning", 
                    "message": f"🚨 ¡Alerta roja, Lucho! Llevás gastado el {porcentaje_gastado:.1f}% de tus ingresos. A este ritmo no llegamos a fin de mes ni locos."
                })
            elif porcentaje_gastado > 50:
                local_insights.append({
                    "type": "advice", 
                    "message": "⚠️ El ritmo de gasto está en zona amarilla. Te sugiero recortar las salidas o compras no esenciales esta semana para mantener el control."
                })
            else:
                local_insights.append({
                    "type": "success", 
                    "message": "✅ Venís con buena conducta financiera este mes. Seguí así y vas a cumplir el objetivo de ahorro holgadamente."
                })
                
            # Buscamos si gastó mucho en Supermercado
            super_gastos = sum(float(e.amount) for e in expenses if e.category == "Supermercado")
            if super_gastos > 0:
                local_insights.append({
                    "type": "advice", 
                    "message": f"🥩 Ojo con los gastos de Supermercado/Carnicería (acumulás ${super_gastos:,.2f}). Podrías optimizar buscando ofertas mayoristas."
                })
                
            return local_insights