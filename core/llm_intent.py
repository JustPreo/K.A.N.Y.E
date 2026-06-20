import json
import ollama

from core.config_loader import get_config


ALLOWED_INTENTS = [
    "open_app", "open_folder", "web_search",
    "activate_mode", "play_music", "close_app", "chat",
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
- No expliques nada. No uses markdown.
- Si hay duda, usa chat.
- Si el usuario pregunta "qué", "cuál", "cómo", "por qué", "crees", "opinas", "recomiendas", usa chat.
- Si el usuario está corrigiendo o continuando una conversación, usa chat.
- Solo usa open_app si claramente pide abrir una app.
- Solo usa close_app si claramente pide cerrar una app.
- Solo usa play_music si claramente pide poner, reproducir o escuchar música.
- Solo usa web_search si claramente pide buscar, googlear o investigar.

Formato obligatorio:
{"intent": "chat", "query": "texto útil"}

Ejemplos:
Usuario: prepárame para jugar -> {"intent": "activate_mode", "query": "gaming"}
Usuario: quiero estudiar -> {"intent": "activate_mode", "query": "estudio"}
Usuario: abre algo para escribir -> {"intent": "open_app", "query": "notas"}
Usuario: cierra brave -> {"intent": "close_app", "query": "brave"}
Usuario: pon runaway kanye west -> {"intent": "play_music", "query": "runaway kanye west"}
Usuario: busca información sobre árboles B -> {"intent": "web_search", "query": "árboles B"}
Usuario: qué opinas de los San Antonio Spurs -> {"intent": "chat", "query": "qué opinas de los San Antonio Spurs"}
Usuario: pero ahorita solo quedan 3 equipos -> {"intent": "chat", "query": "pero ahorita solo quedan 3 equipos"}
"""


def _clean_json(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return ""
    return text[start : end + 1]


def classify_with_llm(user_text: str) -> dict:
    if not user_text:
        return {"intent": "chat", "query": ""}

    config = get_config()
    model_name = config.get("intent_model", "qwen2.5:1.5b")

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            options={"temperature": 0, "num_predict": 80},
        )

        raw = response["message"]["content"].strip()
        cleaned = _clean_json(raw)
        data = json.loads(cleaned)

        intent = data.get("intent", "chat")
        query = data.get("query", user_text)

        if intent not in ALLOWED_INTENTS:
            return {"intent": "chat", "query": user_text}

        return {"intent": intent, "query": query}

    except Exception as error:
        print(f"K.A.N.Y.E.: Error clasificando con LLM: {error}")
        return {"intent": "chat", "query": user_text}
