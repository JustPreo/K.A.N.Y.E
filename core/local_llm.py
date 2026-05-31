import ollama


MODEL_NAME = "qwen2.5:1.5b"


SYSTEM_PROMPT = """
Eres K.A.N.Y.E., un asistente personal local en español.

Tu estilo:
- Responde claro, breve y útil.
- No inventes acciones del sistema.
- Si el usuario pide recomendación, da una respuesta práctica.
- Si el usuario pide abrir apps, carpetas, modos o búsquedas, no ejecutes nada; solo responde conversacionalmente.
- No digas que eres ChatGPT.
"""


conversation_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def ask_llm(user_text: str) -> str:
    if not user_text:
        return "No recibí ninguna pregunta."

    try:
        conversation_history.append({
            "role": "user",
            "content": user_text
        })

        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history,
            options={
                "temperature": 0.7,
                "num_predict": 180
            }
        )

        answer = response["message"]["content"].strip()

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        # Evita que el historial crezca demasiado.
        if len(conversation_history) > 12:
            system_message = conversation_history[0]
            recent_messages = conversation_history[-10:]
            conversation_history.clear()
            conversation_history.append(system_message)
            conversation_history.extend(recent_messages)

        return answer

    except Exception as error:
        return f"No pude conectar con el modelo local. Error: {error}"