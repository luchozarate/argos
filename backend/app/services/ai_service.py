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
        # SDK oficial de Google GenAI para producción
        self.client = genai.Client(api_key=api_key)

    def parse_expense(self, user_text: str) -> ExpenseCreate:
        """
        Toma una entrada de texto plano del usuario y la transforma en un gasto estructurado.
        """
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
            # FAILOVER LOCAL INTELIGENTE POR REGEX (Por si la cuota gratuita de Google se satura)
            print(f"⚠️ Servidor Gemini no disponible ({str(e)}). Procesando con motor analítico local...")
            monto = 1000.00
            text_lower = user_text.lower()
            
            lucas_match = re.search(r'(\d+)\s*luca', text_lower)
            numeros_puros = re.findall(r'\d+', text_lower)
            
            if lucas_match:
                monto = float(lucas_match.group(1)) * 1000
            elif numeros_puros:
                monto = float(numeros_puros[0])
            
            categoria = "Otros"
            if any(p in text_lower for p in ["carne", "super", "comida", "almacen", "verdura", "chino"]):
                categoria = "Supermercado"
            elif any(p in text_lower for p in ["luz", "agua", "gas", "boleta", "factura", "edenor", "metrogas"]):
                categoria = "Servicios"
            elif any(p in text_lower for p in ["nafta", "combustible", "shell", "ypf", "axion"]):
                categoria = "Combustible"
            elif any(p in text_lower for p in ["alquiler", "renta"]):
                categoria = "Alquiler"
            elif any(p in text_lower for p in ["expensa", "expensas"]):
                categoria = "Expensas"

            return ExpenseCreate(
                description=user_text[:40] if user_text else "Gasto Manual",
                category=categoria,
                amount=monto,
                expense_date=date.today()
            )

    def generate_financial_insights(self, expenses: list, income: float) -> list:
        """
        Analiza los gastos consolidados del mes y retorna insights estratégicos breves.
        """
        total_gastado = sum(float(e.amount) for e in expenses)
        resumen_gastos = "".join([f"- {e.description} ({e.category}): ${e.amount}\n" for e in expenses])

        prompt = f"""
        Sos ARGOS, el analista financiero y copiloto personal del usuario. 
        Analizá el ritmo de gasto actual y dale 2 o máximo 3 recomendaciones concisas y bien directas.
        
        Datos:
        - Ingresos: ${income}
        - Gastos: ${total_gastado}
        - Lista de transacciones:
        {resumen_gastos}
        
        Debes responder ÚNICAMENTE con un JSON en este formato:
        {{
            "insights": [
                {{"type": "warning | advice | success", "message": "Tu consejo directo aquí"}}
            ]
        }}
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            data = json.loads(response.text.strip())
            return data["insights"]
        except Exception as e:
            # Fallback analítico local seguro
            local_insights = []
            porcentaje = (total_gastado / income) * 100 if income > 0 else 0
            if porcentaje > 80:
                local_insights.append({"type": "warning", "message": f"🚨 ¡Ojo Lucho! Consumiste el {porcentaje:.1f}% de tus ingresos. Freno de mano urgente."})
            elif porcentaje > 50:
                local_insights.append({"type": "advice", "message": "⚠️ Venimos gastando más de la mitad del sueldo. Bajale a los consumos no esenciales esta semana."})
            else:
                local_insights.append({"type": "success", "message": "✅ El ritmo de ahorro viene excelente este mes. ¡Seguí así!"})
            
            súper_total = sum(float(e.amount) for e in expenses if e.category == "Supermercado")
            if súper_total > 50000:
                local_insights.append({"type": "advice", "message": f"🥩 Registrás ${súper_total:,.2f} en Supermercado/Comida. Podrías optimizar buscando promociones bancarias."})
            return local_insights

    def generate_chat_response(self, user_message: str, expenses: list, income: float) -> str:
        """
        Simula o procesa una conversación interactiva con Jarvis analizando toda la base de datos real.
        """
        total_gastado = sum(float(e.amount) for e in expenses)
        resumen_gastos = "".join([f"- {e.expense_date}: {e.description} ({e.category}) -> ${e.amount}\n" for e in expenses])

        prompt = f"""
        Sos ARGOS (Jarvis), el co-piloto financiero personal del usuario. 
        Tu tono es directo, sumamente inteligente, pragmático, con personalidad argentina amigable pero firme. No andes con vueltas técnicas aburridas.
        
        Datos de la base de datos de este mes:
        - Ingresos de Lucho: ${income}
        - Total gastado: ${total_gastado}
        - Lista de gastos realizados:
        {resumen_gastos}

        Pregunta o duda del usuario: "{user_message}"

        Analizá la lista de gastos reales y dale una respuesta sumamente personalizada. 
        Si te pregunta en qué gastó más, calculale la categoría exacta. 
        Si te pide recortar, dale ideas de recorte sobre sus gastos reales. 
        Si no hay gastos registrados, decile que cargue algo primero.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            # Failover conversacional: analiza de verdad los datos de la DB localmente para responder inteligente
            print(f"⚠️ Error en Gemini Chat ({str(e)}). Ejecutando motor de respuesta local...")
            msg = user_message.lower()
            
            # Agrupar categorías
            categorias = {}
            for e in expenses:
                categorias[e.category] = categorias.get(e.category, 0) + float(e.amount)
            
            cat_mas_cara = max(categorias, key=categorias.get) if categorias else "Ninguna"
            monto_mas_caro = categorias.get(cat_mas_cara, 0) if categorias else 0
            
            if not expenses:
                return "¡Hola Lucho! Todavía no registraste ningún movimiento en este Workspace. Tirame qué compraste hoy y arranco a analizar tu economía."

            if any(x in msg for x in ["gaste", "gasto", "en que", "plata", "mayor"]):
                return f"Lucho, estuve revisando los números. Tu mayor pozo de gasto este mes es **{cat_mas_cara}** con un acumulado de **${monto_mas_caro:,.2f}**. Representa una parte importante de tu presupuesto actual de ${income:,.2f}. ¿Querés que busquemos cómo recortar ahí?"
                
            if any(x in msg for x in ["recortar", "ahorrar", "consejo", "ayuda", "bajar"]):
                comida_gasto = categorias.get("Supermercado", 0) + categorias.get("Comida", 0)
                if comida_gasto > 40000:
                    return f"Analizando tus consumos, el rubro de comidas y supermercado acumula **${comida_gasto:,.2f}**. Ahí hay tierra fértil para recortar: podés evitar los deliveries de fin de semana o aprovechar los días de descuento de las billeteras virtuales."
                return "Te sugiero atacar los gastos hormiga (cafecitos, kioscos, suscripciones que no usás). Parecen pavadas, pero a fin de mes te hacen un agujero gigante en el saldo."

            return f"Acá ARGOS, Lucho. Actualmente tenés ${total_gastado:,.2f} gastados de tus ${income:,.2f} disponibles. Estoy listo para ayudarte a auditar tus gastos fijos o planificar el próximo mes. ¿Por dónde querés arrancar?"