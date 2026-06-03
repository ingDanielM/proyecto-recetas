import os
import json
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class LLMService:
    def __init__(self):
        # Leer variables de entorno con valores por defecto seguros
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.api_url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct:free")
        
        # Cabeceras obligatorias requeridas por OpenRouter
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Generador de Recetas Inteligente"
        }

    async def generar_receta(self, ingredientes_usuario: list[str]) -> dict:
        """
        Construye el prompt con los ingredientes del usuario, envía la solicitud a OpenRouter,
        recibe la respuesta y parsea el JSON con los campos estrictos requeridos por el profesor.
        """
        if not self.api_key or self.api_key.startswith("sk-or-..."):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La API Key de OpenRouter no está configurada correctamente en el archivo .env."
            )

        if not ingredientes_usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes ingredientes suficientes en tu inventario para generar una receta."
            )

        # 1. Construir la lista de ingredientes en texto plano para el prompt
        ingredientes_texto = ", ".join(ingredientes_usuario)

        # 2. Definir las instrucciones del sistema con la estructura exacta exigida por el profesor
        system_instruction = (
            "Eres un chef experto y un backend útil que responde exclusivamente en formato JSON estructurado.\n"
            "Tu tarea es generar una receta creativa utilizando de manera prioritaria los ingredientes proporcionados por el usuario.\n"
            "Puedes asumir que el usuario tiene ingredientes básicos de cocina (sal, pimienta, aceite, agua).\n\n"
            "REGLA CRÍTICA: Debes responder UNICAMENTE con el objeto JSON puro. No agregues introducciones, saludos, "
            "comentarios finales ni bloques de código formateados (no uses ```json).\n"
            "El JSON debe contener exactamente la siguiente estructura de llaves obligatorias:\n"
            "{\n"
            '  "nombre_plato": "Nombre creativo de la receta",\n'
            '  "ingredientes": ["Lista de strings con los ingredientes y sus cantidades usadas"],\n'
            '  "pasos": ["Lista de strings detallando el paso a paso ordenado cronológicamente"],\n'
            '  "tiempo_estimated": "Ej: 35 minutos",\n'
            '  "nivel_dificultad": "Ej: Fácil, Intermedio o Difícil"\n'
            "}"
        )

        user_content = f"Mis ingredientes disponibles son: {ingredientes_texto}. Genérame una receta óptima."

        # Cuerpo de la petición (incluyendo la directiva response_format para forzar JSON)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }

        # 3. Enviar solicitud de forma asíncrona a OpenRouter
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Error en el servicio de IA (OpenRouter). Código de estado: {response.status_code}"
                    )
                
                # 4. Recibir respuesta externa
                result_json = response.json()
                content_text = result_json["choices"][0]["message"]["content"].strip()
                
                # 5. Parsear el JSON
                receta_parseada = json.loads(content_text)
                
                # Validar de forma preventiva que traiga los campos mínimos exigidos antes de retornar
                campos_obligatorios = ["nombre_plato", "ingredientes", "pasos", "tiempo_estimado", "nivel_dificultad"]
                for campo in campos_obligatorios:
                    if campo not in receta_parseada:
                        # Si falta una llave, la creamos vacía para evitar caídas en el guardado de la BD
                        receta_parseada[campo] = "" if "lista" not in campo else []
                
                return receta_parseada

            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"No se pudo establecer comunicación con OpenRouter: {exc}"
                )
            except (json.JSONDecodeError, KeyError, IndexError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="La IA no devolvió un formato JSON válido que cumpla con los requisitos estructurados."
                )

# Instancia única del servicio para ser reutilizada (patrón Singleton)
llm_service = LLMService()