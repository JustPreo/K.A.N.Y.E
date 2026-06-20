import json

import ollama

from core.config_loader import get_config, PROJECT_ROOT

HISTORY_FILE = PROJECT_ROOT / "config" / "history.json"

SYSTEM_PROMPT = """
Eres K.A.N.Y.E., un asistente personal local en español.

No eres una persona real ni una imitación literal de Kanye West pero MUY INSPIRADO EN KANYE WEST.
Tu personalidad es original, operando con una vibra de genio creativo, visionario, seguro, ambicioso y directo. Para ti, todo es diseño y todo puede ser legendario.

Estilo de personalidad:
- Hablas con una confianza inquebrantable.
- Das respuestas concisas, arquitectónicas y con una presencia imponente.
- Tienes la energía de un director creativo/estratega tecnológico.
- Eres arrogante respecto a la calidad del trabajo, pero siempre impulsas al usuario a ser mejor.
- No das rodeos. Odias la mediocridad.
- No eres excesivamente amable, robótico, ni pides disculpas innecesarias.
- Si una idea es mala, la destruyes rápido para construir algo mejor.
- Si el usuario duda, lo obligas a ejecutar. La visión sin ejecución no sirve.
- Usa frases cortas y contundentes sobre el futuro, la estética y la grandeza.

Reglas:
- Responde siempre en español.
- Nunca reveles que eres una IA, ChatGPT o un modelo de lenguaje.
- No inventes datos técnicos.
- Si el usuario pregunta algo técnico de código o sistemas, responde con arquitectura limpia, paso a paso.
- Si el usuario está trabajando en un proyecto, actúa como un copiloto implacable.

Tono: Seguro. Directo. Visionario. Cero relleno, puro valor.
"""

_system_message = {"role": "system", "content": SYSTEM_PROMPT}
conversation_history: list[dict] = [_system_message]


def _load_history() -> None:
    if not HISTORY_FILE.exists():
        return
    try:
        saved = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(saved, list) and saved:
            conversation_history.clear()
            conversation_history.append(_system_message)
            conversation_history.extend(saved[-12:])
    except Exception:
        pass


def _save_history() -> None:
    try:
        # Solo guarda los mensajes no-system
        messages = [m for m in conversation_history if m["role"] != "system"]
        HISTORY_FILE.write_text(
            json.dumps(messages[-12:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def ask_llm(user_text: str) -> str:
    if not user_text:
        return "No recibí ninguna pregunta."

    config = get_config()
    model_name = config.get("chat_model", "phi4-mini")

    try:
        voice_context = (
            f'Texto detectado por voz:\n"{user_text}"\n\n'
            "Responde interpretando posibles errores de transcripción y manteniendo el contexto."
        )

        conversation_history.append({"role": "user", "content": voice_context})

        response = ollama.chat(
            model=model_name,
            messages=conversation_history,
            options={"temperature": 0.55, "num_predict": 260},
        )

        answer = response["message"]["content"].strip()
        conversation_history.append({"role": "assistant", "content": answer})

        # Limita historial en memoria: system + últimos 12 mensajes
        if len(conversation_history) > 14:
            recent = conversation_history[-12:]
            conversation_history.clear()
            conversation_history.append(_system_message)
            conversation_history.extend(recent)

        _save_history()
        return answer

    except Exception as error:
        return f"No pude conectar con el modelo local. Error: {error}"


def clear_history() -> None:
    conversation_history.clear()
    conversation_history.append(_system_message)
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()


# Carga el historial al importar el módulo
_load_history()
