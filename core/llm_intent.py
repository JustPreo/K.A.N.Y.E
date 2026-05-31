import json
import ollama


MODEL_NAME = "qwen2.5:1.5b"


ALLOWED_INTENTS = [
    "open_app",
    "open_folder",
    "web_search",
    "activate_mode",
    "chat"
]


SYSTEM_PROMPT = """
Eres un clasificador de intención para un asistente local llamado K.A.N.Y.E.

Tu única tarea es convertir el texto del usuario en JSON válido.

Intenciones permitidas:
- open_app: abrir una aplicación
- open_folder: abrir una carpeta
- web_search: buscar algo en internet
- activate_mode: activar un modo guardado
- chat: conversación normal, recomendación o pregunta general

Reglas:
- Responde SOLO con JSON válido.
- No expliques nada.
- No uses markdown.
- No inventes apps raras si no es claro.
- Si el usuario pregunta opinión, recomendación, explicación o conversación, usa chat.
- Si el usuario dice algo como "prepárame para jugar", usa activate_mode con query "gaming".
- Si dice "quiero estudiar", usa activate_mode con query "estudio".
- Si dice "voy a programar", usa activate_mode con query "programacion".
- Si dice "busca", "investiga" o "googlea", usa web_search.

Formato obligatorio:
{
  "intent": "chat",
  "query": "texto útil"
}

Ejemplos:
Usuario: prepárame para jugar
Respuesta:
{"intent": "activate_mode", "query": "gaming"}

Usuario: quiero estudiar cálculo
Respuesta:
{"intent": "activate_mode", "query": "estudio"}

Usuario: quiero programar un rato
Respuesta:
{"intent": "activate_mode", "query": "programacion"}

Usuario: busca información sobre árboles B
Respuesta:
{"intent": "web_search", "query": "árboles B"}

Usuario: qué opinas de los San Antonio Spurs
Respuesta:
{"intent": "chat", "query": "qué opinas de los San Antonio Spurs"}

Usuario: abre algo para escribir
Respuesta:
{"intent": "open_app", "query": "notas"}
"""


def classify_with_llm(user_text: str) -> dict:
    if not user_text:
        return {
            "intent": "chat",
            "query": ""
        }

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 80
            }
        )

        raw_answer = response["message"]["content"].strip()

        data = json.loads(raw_answer)

        intent = data.get("intent", "chat")
        query = data.get("query", user_text)

        if intent not in ALLOWED_INTENTS:
            intent = "chat"
            query = user_text

        return {
            "intent": intent,
            "query": query
        }

    except Exception as error:
        print(f"K.A.N.Y.E.: Error clasificando intención con LLM: {error}")

        return {
            "intent": "chat",
            "query": user_text
        }