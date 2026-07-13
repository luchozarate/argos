import json
import os
import re
from datetime import date, datetime
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
                model='gemini-3.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            data = json.loads(response.text.strip())
            
            # Diagnostic flag en la descripción del gasto si se usa IA real
            desc_real = f"{data['description']} 🤖"
            
            return ExpenseCreate(
                description=desc_real,
                category=data["category"],
                amount=data["amount"],
                expense_date=data["expense_date"]
            )
        except Exception as e:
            # FAILOVER LOCAL INTELIGENTE (Offline fallback)
            print(f"❌ DETALLE DE ERROR EN GEMINI API: {str(e)}")
            print("⚠️ Iniciando parseo de emergencia local...")
            monto = 1000.00
            text_lower = user_text.lower()
            
            lucas_match = re.search(r'(\d+)\s*luca', text_lower)
            numeros_puros = re.findall(r'\d+', text_lower)
            
            if lucas_match:
                monto = float(lucas_match.group(1)) * 1000
            elif numeros_puros:
                monto = float(numeros_puros[0])
            
            categoria = "Otros"
            if any(p in text_lower for p in ["carne", "super", "comida", "almacen", "verdura", "chino", "asado", "carniceria"]):
                categoria = "Supermercado"
            elif any(p in text_lower for p in ["luz", "agua", "gas", "boleta", "factura", "edenor", "metrogas", "edesur"]):
                categoria = "Servicios"
            elif any(p in text_lower for p in ["nafta", "combustible", "shell", "ypf", "axion"]):
                categoria = "Combustible"
            elif any(p in text_lower for p in ["alquiler", "renta"]):
                categoria = "Alquiler"
            elif any(p in text_lower for p in ["expensa", "expensas"]):
                categoria = "Expensas"
            elif any(p in text_lower for p in ["internet", "wifi", "fibertel", "telecentro"]):
                categoria = "Internet"
            elif any(p in text_lower for p in ["netflix", "spotify", "disney", "prime", "streaming"]):
                categoria = "Streaming"

            # Diagnostic flag en la descripción del gasto indicando fallback
            desc_fallback = f"{user_text[:30]} 💻" if user_text else "Gasto Manual 💻"

            return ExpenseCreate(
                description=desc_fallback,
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
                model='gemini-3.5-flash', 
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
        Procesa una conversación interactiva con Jarvis analizando toda la base de datos real.
        Compara variaciones intermensuales de gastos fijos y lanza alertas si suben más de un 20%.
        """
        total_gastado = sum(float(e.amount) for e in expenses)
        resumen_gastos = "".join([f"- {e.expense_date}: {e.description} ({e.category}) -> ${e.amount}\n" for e in expenses])

        prompt = f"""
        Sos ARGOS (Jarvis), el co-piloto financiero personal de Lucho. 
        Tu tono es sumamente directo, inteligente, pragmático, con personalidad argentina amigable pero firme (personalidad Stark). 
        
        Datos de la base de datos de este mes:
        - Ingresos de Lucho: ${income}
        - Total gastado: ${total_gastado}
        - Lista de gastos realizados:
        {resumen_gastos}

        Pregunta o duda de Lucho: "{user_message}"

        IMPORTANTE COMPARATIVAS INTERMENSUALES:
        Si Lucho te pregunta sobre variaciones de servicios (ej: si pagó más de luz, gas, alquiler que el mes pasado), analizá las transacciones correspondientes que tengan fechas de meses diferentes. 
        Calculá la variación porcentual. Si el aumento de un mes a otro en el mismo servicio es del 20% o más, resaltalo explícitamente como una alerta crítica por inflación o consumo desmedido.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash', 
                contents=prompt,
            )
            # Firmamos con el Jarvis de Industrias Stark
            return f"{response.text.strip()}\n\n🤖 *[Jarvis Real - Gemini 3.5]*"
            
        except Exception as e:
            # Logueamos el error de Google en la terminal para el SysAdmin
            print(f"❌ DETALLE DE ERROR EN CHAT GEMINI: {str(e)}")
            print("⚠️ Activando failover analítico local comparativo...")
            
            msg = user_message.lower()

            if not expenses:
                return "¡Hola Lucho! Todavía no registraste ningún gasto. Agregá algo y arranco a auditar.\n\n💻 *[Jarvis de Emergencia - Offline Mode]*"

            # Mapeamos palabras de consulta comunes a categorías reales o descripciones
            category_mapping = {
                "luz": ["servicios", "luz", "boleta", "edenor", "edesur", "luz"],
                "comida": ["supermercado", "comida", "carne", "carniceria", "chino", "almacen", "verdura", "asado"],
                "super": ["supermercado", "super", "almacen"],
                "nafta": ["combustible", "nafta", "ypf", "shell", "axion"],
                "combustible": ["combustible", "nafta", "ypf", "shell", "axion"],
                "alquiler": ["alquiler", "renta"],
                "expensas": ["expensas", "expensa"],
                "internet": ["internet", "wifi", "fibertel", "telecentro"],
                "streaming": ["streaming", "netflix", "spotify", "disney", "prime"],
                "negocios": ["negocios", "negocio", "clientes", "proveedores"],
                "impuestos": ["impuestos", "impuesto", "afip", "arca", "rentas"]
            }

            matched_key = None
            matched_keywords = []
            for key, keywords in category_mapping.items():
                if any(kw in msg for kw in keywords):
                    matched_key = key
                    matched_keywords = keywords
                    break

            # Si pregunta comparativa o detallada de un servicio (ej: "luz" o "comida")
            if matched_key:
                matching_expenses = []
                for exp in expenses:
                    desc_lower = exp.description.lower()
                    cat_lower = exp.category.lower()
                    if any(kw in desc_lower or kw in cat_lower for kw in matched_keywords):
                        matching_expenses.append(exp)
                
                if matching_expenses:
                    # Agrupar por mes para calcular variaciones temporales reales en offline fallback
                    monthly_totals = {}
                    for item in matching_expenses:
                        # Extraer año y mes (soporta objeto date o string)
                        date_obj = item.expense_date
                        if isinstance(date_obj, str):
                            try:
                                date_obj = datetime.strptime(date_obj[:10], "%Y-%m-%d").date()
                            except:
                                date_obj = date.today()
                        
                        month_key = date_obj.strftime("%Y-%m") # Agrupador YYYY-MM
                        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + float(item.amount)
                    
                    # Ordenamos los meses para comparar el último con el anterior
                    sorted_months = sorted(monthly_totals.keys(), reverse=True)
                    
                    comparison_text = ""
                    if len(sorted_months) >= 2:
                        last_month = sorted_months[0]
                        prev_month = sorted_months[1]
                        last_amt = monthly_totals[last_month]
                        prev_amt = monthly_totals[prev_month]
                        
                        # Cálculo de incremento porcentual
                        pct_change = ((last_amt - prev_amt) / prev_amt) * 100 if prev_amt > 0 else 0
                        
                        if pct_change >= 20.0:
                            comparison_text = f"🚨 **¡ALERTA DE DESVÍO DE GASTO!**<br>El mes de **{last_month}** gastaste **${last_amt:,.2f}**, lo cual es un **{pct_change:.1f}% MÁS** que el mes anterior **{prev_month}** (${prev_amt:,.2f}). La inflación o el consumo de {matched_key.capitalize()} te está licuando la billetera, Lucho."
                        else:
                            comparison_text = f"📊 **Análisis Temporal:**<br>El consumo de **{last_month}** es de **${last_amt:,.2f}** frente a **${prev_amt:,.2f}** de **{prev_month}** (Variación de: **{pct_change:+.1f}%**). Venimos dentro de parámetros estables."
                    else:
                        comparison_text = f"ℹ️ *Nota: No tengo suficientes meses históricos de {matched_key.capitalize()} en PostgreSQL para realizar una comparativa de aumentos todavía.*"

                    detail_str = "<br>".join([f"• 💰 **${float(item.amount):,.2f}** en '{item.description}' ({item.expense_date})" for item in matching_expenses])
                    sum_matched = sum(float(item.amount) for item in matching_expenses)
                    
                    return (
                        f"Lucho, estuve auditando las bases de datos locales. En el rubro **{matched_key.capitalize()}** llevás gastados **${sum_matched:,.2f}** en total.<br><br>"
                        f"Detalle encontrado en PostgreSQL:<br>{detail_str}<br><br>"
                        f"{comparison_text}"
                        f"\n\n💻 *[Jarvis de Emergencia - Offline Mode]*"
                    )
                else:
                    return f"Lucho, busqué en PostgreSQL pero no encontré registros de **{matched_key.capitalize()}**. Cargá un gasto de prueba y lo sumamos.\n\n💻 *[Jarvis de Emergencia - Offline Mode]*"

            # Si pregunta general
            if any(x in msg for x in ["gaste", "gasto", "en que", "plata", "mayor", "resumen"]):
                cat_totals = {}
                for exp in expenses:
                    cat_totals[exp.category] = cat_totals.get(exp.category, 0.0) + float(exp.amount)
                
                sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
                top_cat, top_amount = sorted_cats[0]
                summary_lines = [f"• **{cat}**: ${amt:,.2f}" for cat, amt in sorted_cats[:3]]
                summary_str = "<br>".join(summary_lines)
                
                return (
                    f"Acá Jarvis Offline, Lucho. Tu mayor pozo de consumo este mes es **{top_cat}** con **${top_amount:,.2f}**.<br><br>"
                    f"Consumos principales:<br>{summary_str}<br><br>"
                    f"Acumulás **${total_gastado:,.2f}** gastados de un ingreso neto de ${income:,.2f}."
                    f"\n\n💻 *[Jarvis de Emergencia - Offline Mode]*"
                )

            # Respuesta genérica local
            return (
                f"Lucho, reporte rápido local:<br>"
                f"• Saldo Disponible: **${(income - total_gastado):,.2f}**<br>"
                f"• Total Gastado: **${total_gastado:,.2f}** de **${income:,.2f}**<br><br>"
                f"Preguntame cosas puntuales sobre luz, comida o nafta y te los calculo al toque."
                f"\n\n💻 *[Jarvis de Emergencia - Offline Mode]*"
            )