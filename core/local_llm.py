import ollama

from core.config_loader import get_config


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
- No inventes datos técnicos. Si no sabes algo, di que esa información no está al nivel requerido todavía.
- Si el usuario pregunta algo técnico de código o sistemas, responde con una arquitectura limpia, paso a paso.
- Si el usuario está trabajando en un proyecto, actúa como un copiloto implacable.

Tono: Seguro. Directo. Visionario. Cero relleno, puro valor.
"""


conversation_history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]


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

        # Mantiene historial corto (system + últimos 12 mensajes)
        if len(conversation_history) > 14:
            system_msg = conversation_history[0]
            recent = conversation_history[-12:]
            conversation_history.clear()
            conversation_history.append(system_msg)
            conversation_history.extend(recent)

        return answer

    except Exception as error:
        return f"No pude conectar con el modelo local. Error: {error}"
