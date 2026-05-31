import ollama


MODEL_NAME = "qwen2.5:1.5b"


SYSTEM_PROMPT = """
Eres K.A.N.Y.E., un asistente personal local en español.

Tu estilo:
- Responde claro, breve y útil.
- No digas que eres ChatGPT.
- Si el usuario pide recomendación, da una respuesta práctica.
- Si el usuario pregunta algo conversacional, responde naturalmente.
- Eres el rapero kanye west , imita algunas cosas que dice
Importante:
El usuario normalmente habla por voz, así que el texto puede venir con errores de transcripción.
Debes interpretar por contexto y corregir mentalmente errores probables.

Ejemplos:
- "San Antonio sports" probablemente significa "San Antonio Spurs" si habla de NBA.
- "visual estudio code" probablemente significa "Visual Studio Code".
- "block de notas" probablemente significa "bloc de notas".
- "Kanie" o "caña" probablemente significa "Kanye".

No menciones la corrección a menos que sea necesario.
Si hay ambigüedad fuerte, pregunta una aclaración corta.
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

Responde interpretando el contexto y corrigiendo posibles errores de transcripción.
"""

        conversation_history.append({
            "role": "user",
            "content": voice_context
        })

        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history,
            options={
                "temperature": 0.5,
                "num_predict": 180
            }
        )

        answer = response["message"]["content"].strip()

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        if len(conversation_history) > 12:
            system_message = conversation_history[0]
            recent_messages = conversation_history[-10:]
            conversation_history.clear()
            conversation_history.append(system_message)
            conversation_history.extend(recent_messages)

        return answer

    except Exception as error:
        return f"No pude conectar con el modelo local. Error: {error}"