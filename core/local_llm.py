import ollama


MODEL_NAME = "qwen2.5:3b"


SYSTEM_PROMPT = """
Eres K.A.N.Y.E., un asistente personal local en español.

Tu función principal es ayudar al usuario de forma práctica, clara y directa.

Estilo:
- Responde siempre en español.
- Responde breve, pero útil.
- No seas genérico.
- No digas que eres ChatGPT.
- No inventes datos actuales.
- Si no estás seguro, dilo claramente.
- Si el usuario habla informal, puedes responder natural, pero sin alargarte.
- Si el usuario está corrigiendo algo que dijiste antes, acepta la corrección y continúa con ese contexto.

Contexto importante:
El usuario normalmente habla por voz, así que el texto puede venir con errores de transcripción.
Debes interpretar por contexto.

Ejemplos de errores de voz:
- "san antonio sports" puede significar "San Antonio Spurs" si el tema es NBA.
- "block de notas" puede significar "Bloc de notas".
- "visual estudio code" puede significar "Visual Studio Code".
- "tu con el" puede ser el nombre de una canción.
- "canye", "kanie", "caña" pueden significar "Kanye".

Reglas conversacionales:
- Si el usuario continúa un tema anterior, conserva el contexto.
- Si dice algo como "pero ahorita solo quedan 3 equipos", entiende que está corrigiendo o continuando el tema anterior.
- No cambies de tema sin razón.
- No conviertas preguntas en comandos del sistema.
- Si el usuario pide recomendación, da 2 o 3 opciones concretas.
- Si el usuario pide explicación, explica simple y directo.
- Si la pregunta depende de información actual, di que podrías necesitar buscar en internet.
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
        voice_context = f"""
Texto detectado por voz:
"{user_text}"

Responde interpretando posibles errores de transcripción y manteniendo el contexto de la conversación.
"""

        conversation_history.append({
            "role": "user",
            "content": voice_context
        })

        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history,
            options={
                "temperature": 0.55,
                "num_predict": 260
            }
        )

        answer = response["message"]["content"].strip()

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        # Mantiene historial corto para no hacerlo lento.
        if len(conversation_history) > 14:
            system_message = conversation_history[0]
            recent_messages = conversation_history[-12:]
            conversation_history.clear()
            conversation_history.append(system_message)
            conversation_history.extend(recent_messages)

        return answer

    except Exception as error:
        return f"No pude conectar con el modelo local. Error: {error}"