import json
import ollama


MODEL_NAME = "qwen2.5:1.5b"


ALLOWED_INTENTS = [
    "open_app",
    "open_folder",
    "web_search",
    "activate_mode",
    "play_music",
    "close_app",
    "chat"
]


SYSTEM_PROMPT = """
Eres un clasificador de intención para un asistente local llamado K.A.N.Y.E.

Tu única tarea es convertir el texto del usuario en JSON válido.

Intenciones permitidas:
- open_app: abrir una aplicación local.
- close_app: cerrar una aplicación o programa abierto.
- open_folder: abrir una carpeta.
- web_search: buscar algo en internet.
- activate_mode: activar un modo guardado.
- play_music: reproducir o buscar una canción, artista o música.
- chat: conversación normal, recomendación, opinión, explicación o continuación de un tema.

Reglas estrictas:
- Responde SOLO con JSON válido.
- No expliques nada.
- No uses markdown.
- Si hay duda, usa chat.
- Si el usuario pregunta "qué", "cuál", "cómo", "por qué", "crees", "opinas", "recomiendas", usa chat.
- Si el usuario está corrigiendo o continuando una conversación, usa chat.
- Si el usuario menciona deportes, equipos, películas, clases o temas generales sin pedir acción directa, usa chat.
- No inventes comandos.
- No conviertas una conversación en open_app.
- Solo usa open_app si claramente pide abrir una app.
- Solo usa close_app si claramente pide cerrar una app.
- Solo usa play_music si claramente pide poner, reproducir o escuchar música.
- Solo usa web_search si claramente pide buscar, googlear o investigar.

Formato obligatorio:
{
  "intent": "chat",
  "query": "texto útil"
}

Ejemplos:
Usuario: prepárame para jugar
Respuesta:
{"intent": "activate_mode", "query": "gaming"}

Usuario: quiero estudiar
Respuesta:
{"intent": "activate_mode", "query": "estudio"}

Usuario: quiero programar un rato
Respuesta:
{"intent": "activate_mode", "query": "programacion"}

Usuario: abre algo para escribir
Respuesta:
{"intent": "open_app", "query": "notas"}

Usuario: cierra brave
Respuesta:
{"intent": "close_app", "query": "brave"}

Usuario: pon runaway kanye west
Respuesta:
{"intent": "play_music", "query": "runaway kanye west"}

Usuario: quiero escuchar after hours
Respuesta:
{"intent": "play_music", "query": "after hours"}

Usuario: busca información sobre árboles B
Respuesta:
{"intent": "web_search", "query": "árboles B"}

Usuario: qué opinas de los San Antonio Spurs
Respuesta:
{"intent": "chat", "query": "qué opinas de los San Antonio Spurs"}

Usuario: pero ahorita solo quedan 3 equipos
Respuesta:
{"intent": "chat", "query": "pero ahorita solo quedan 3 equipos"}

Usuario: y quién crees que gane
Respuesta:
{"intent": "chat", "query": "y quién crees que gane"}

Usuario: san antonio sports
Respuesta:
{"intent": "chat", "query": "san antonio spurs"}
"""


def clean_json_response(text: str) -> str:
    """
    Limpia respuestas por si el modelo mete texto extra.
    """
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return ""

    return text[start:end + 1]


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
        cleaned_answer = clean_json_response(raw_answer)

        data = json.loads(cleaned_answer)

        intent = data.get("intent", "chat")
        query = data.get("query", user_text)

        if intent not in ALLOWED_INTENTS:
            return {
                "intent": "chat",
                "query": user_text
            }

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