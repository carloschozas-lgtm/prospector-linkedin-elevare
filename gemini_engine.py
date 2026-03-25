import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# SOLUCIÓN: Usamos el alias flash-latest que está disponible en la lista de modelos
model = genai.GenerativeModel('gemini-flash-latest')

def analizar_perfil_linkedin(texto_perfil, linea_negocio, cargo_objetivo, dolor_objetivo):
    """
    Motor real conectado a Gemini API (Versión Flash).
    """
    system_instruction = """
    Eres ELEVARE SMART LEADS Engine, un motor de Sales Intelligence de élite. 
    TU MISIÓN: Analizar perfiles de LinkedIn con precisión quirúrgica para determinar si son el Ideal Customer Profile (ICP) y redactar el mensaje de apertura perfecto.

    CRITERIOS DE CALIFICACIÓN (Lead Scoring 0-100):
    - 90-100: Cargo exacto, industria perfecta, señales claras de dolor.
    - 70-89: Cargo relacionado, industria compatible, potencial interés.
    - <50: No es ICP.

    ESTILO DE REDACCIÓN (Social Selling 3.0):
    - No uses "Espero que estés bien". 
    - Sé directo, breve (<280 caracteres) y ultra-personalizado.
    - Menciona un logro, una palabra clave del perfil o una conexión lógica real.
    - Tono: Sofisticado, profesional y disruptivo.
    """
    
    prompt = f"""
    {system_instruction}
    
    CONTEXTO DE LA CAMPAÑA:
    - Línea de Negocio: {linea_negocio}
    - Cargo Objetivo: {cargo_objetivo}
    - Dolor a detectar: {dolor_objetivo}
    
    DATOS DEL PROSPECTO (LinkedIn):
    {texto_perfil}
    
    INSTRUCCIONES DE SALIDA:
    Analiza fríamente si tiene sentido contactarlo. Si el score es <60, 'es_icp' debe ser false.
    Devuelve estrictamente un JSON válido con esta estructura:
    {{
        "es_icp": boolean,
        "score": integer (0-100),
        "analisis_detalle": "Breve explicación de por qué este score y qué ángulo de ataque usar",
        "dolor_detectado": "El problema específico que identificaste en su perfil",
        "resumen_contexto": "3-4 palabras que definan al prospecto",
        "mensaje_sugerido": "Mensaje de contacto listo para enviar"
    }}
    """
    try:
        response = model.generate_content(
            prompt, 
            generation_config={
                "response_mime_type": "application/json", 
                "temperature": 0.2
            }
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Error en API Gemini: {str(e)}"}

def generar_seguimiento(contexto_original, mensaje_anterior, paso_actual, canal):
    """
    Genera un mensaje de seguimiento coherente con el contacto previo.
    """
    prompt = f"""
    Eres THEOS-Core. Debes redactar un mensaje de seguimiento (Paso {paso_actual}) para un prospecto.
    
    CONTEXTO INICIAL: {contexto_original}
    MENSAJE ANTERIOR: {mensaje_anterior}
    CANAL ACTUAL: {canal}
    
    REGLAS:
    1. Mantén la coherencia con lo hablado anteriormente.
    2. No seas insistente ni molesto. 
    3. Agrega valor o haz una pregunta breve que invite a la acción.
    4. < 250 caracteres.
    5. No uses saludos genéricos.
    
    Devuelve solo el texto del mensaje.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generando seguimiento: {str(e)}"
