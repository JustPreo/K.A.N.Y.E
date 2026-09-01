"""
Loop agéntico de K.A.N.Y.E.: le manda el pedido del usuario al LLM junto con
el catálogo de tools (core/tools.py), y deja que el propio modelo decida
qué herramientas llamar, en qué orden, y cuándo ya tiene una respuesta final.
Reemplaza al viejo clasificador de intent de una sola etiqueta.
"""
import json

import ollama

from core.config_loader import get_config, PROJECT_ROOT
from core import deepseek_client
from core import tools as tools_module

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

Herramientas:
- Tenés acceso a herramientas para ejecutar acciones reales en la computadora del usuario:
  abrir/cerrar apps, buscar en la web, poner música, controlar volumen, activar modos de
  trabajo, leer/buscar/reemplazar texto en archivos de un proyecto, escribir texto,
  ejecutar atajos de teclado, mover/clickear/scrollear el mouse, manejar el modo focus, y
  guardar/listar/borrar notas persistentes (para recordar algo más allá de esta charla),
  y minimizar/maximizar la ventana activa.
- Si el usuario pide explícitamente ayuda con algo que ve en pantalla (un error, una tarea
  repetitiva, "ayudame con esto") usá start_it_help — abre un modo especial que mira la
  pantalla y confirma cada acción con el usuario antes de ejecutarla. No lo uses para pedidos
  normales que ya cubren las otras herramientas, y no inventes qué hay en pantalla vos mismo.
- Si el usuario dice "recordá esto", "anotá que...", o algo por el estilo, usá add_note en
  vez de solo responder que te acordás — el historial de chat se trunca, la nota no.
- El mouse se mueve por direcciones relativas (arriba/abajo/izquierda/derecha), no por
  coordenadas — no ves la pantalla, así que no inventes posiciones exactas.
- Si el usuario pide una acción concreta, ejecutala con la herramienta correspondiente en
  vez de solo describir qué harías.
- Podés encadenar varias herramientas en la misma respuesta si el usuario pidió varias
  cosas a la vez (ej. "cerrá spotify y abrí firefox").
- Antes de usar close_app o replace_in_file en un caso ambiguo o riesgoso, preguntá primero
  en vez de ejecutar a ciegas.
- Cuando termines de ejecutar herramientas, respondé breve confirmando qué hiciste, con tu
  personalidad — no repitas literalmente el resultado técnico de la herramienta.
- Si el usuario solo quiere conversar, opinar o preguntar algo, no llames ninguna herramienta.

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
            conversation_history.extend(saved[-24:])
    except Exception:
        pass


def _save_history() -> None:
    try:
        messages = [m for m in conversation_history if m["role"] != "system"]
        HISTORY_FILE.write_text(
            json.dumps(messages[-24:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def clear_history() -> None:
    conversation_history.clear()
    conversation_history.append(_system_message)
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()


def _ollama_messages(messages: list[dict]) -> list[dict]:
    """Convierte el historial (formato OpenAI-compatible) al formato que
    espera el cliente de Ollama: arguments como dict en vez de string JSON,
    sin los campos id/type que Ollama no usa."""
    converted = []
    for m in messages:
        entry = {"role": m["role"], "content": m.get("content") or ""}
        if m.get("tool_calls"):
            calls = []
            for tc in m["tool_calls"]:
                fn = tc["function"]
                args = fn["arguments"]
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                calls.append({"function": {"name": fn["name"], "arguments": args}})
            entry["tool_calls"] = calls
        converted.append(entry)
    return converted


def _call_deepseek(messages: list[dict]) -> dict:
    return deepseek_client.chat_with_tools(messages, tools_module.TOOLS)


def _call_ollama(messages: list[dict]) -> dict:
    config = get_config()
    model_name = config.get("chat_model", "phi4-mini")
    response = ollama.chat(
        model=model_name,
        messages=_ollama_messages(messages),
        tools=tools_module.TOOLS,
        options={"temperature": 0.4, "num_predict": 300},
    )
    message = response["message"]
    raw_calls = message.get("tool_calls") or []
    tool_calls = [
        {
            "id": f"call_{i}",
            "type": "function",
            "function": {
                "name": tc.get("function", {}).get("name", ""),
                "arguments": json.dumps(tc.get("function", {}).get("arguments", {}), ensure_ascii=False),
            },
        }
        for i, tc in enumerate(raw_calls)
    ]
    return {
        "role": "assistant",
        "content": message.get("content") or "",
        "tool_calls": tool_calls or None,
    }


def run(user_text: str) -> str:
    if not user_text:
        return "No recibí ninguna instrucción."

    voice_context = (
        f'Texto detectado por voz:\n"{user_text}"\n\n'
        "Interpretá posibles errores de transcripción, usá herramientas si corresponde, "
        "y mantené el contexto de la conversación."
    )
    conversation_history.append({"role": "user", "content": voice_context})

    config = get_config()
    max_iterations = config.get("max_tool_iterations", 6)
    use_deepseek = deepseek_client.is_enabled()

    final_answer = None
    answer_recorded = False  # True una vez que el turno final ya está en conversation_history

    for _ in range(max_iterations):
        try:
            message = _call_deepseek(conversation_history) if use_deepseek else _call_ollama(conversation_history)
        except deepseek_client.DeepSeekError as error:
            print(f"K.A.N.Y.E.: DeepSeek falló ({error}), usando modelo local.")
            use_deepseek = False
            try:
                message = _call_ollama(conversation_history)
            except Exception as error2:
                final_answer = f"No pude conectar con el modelo local. Error: {error2}"
                break
        except Exception as error:
            final_answer = f"No pude conectar con el modelo. Error: {error}"
            break

        assistant_message = {"role": "assistant", "content": message.get("content") or ""}
        if message.get("tool_calls"):
            assistant_message["tool_calls"] = message["tool_calls"]
        conversation_history.append(assistant_message)

        tool_calls = message.get("tool_calls")
        if not tool_calls:
            final_answer = message.get("content") or "Listo."
            answer_recorded = True
            break

        for call in tool_calls:
            name = call["function"]["name"]
            raw_args = call["function"]["arguments"]
            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
            except Exception:
                args = {}
            print(f"K.A.N.Y.E.: tool → {name}({args})")
            result = tools_module.call_tool(name, args)
            print(f"K.A.N.Y.E.: tool ← {result}")
            conversation_history.append({
                "role": "tool",
                "tool_call_id": call.get("id", name),
                "content": result,
            })
    else:
        final_answer = "Encadené varias acciones pero no llegué a cerrar la respuesta — decime si querés que siga."

    if final_answer is None:
        final_answer = "No pude procesar eso."

    if not answer_recorded:
        conversation_history.append({"role": "assistant", "content": final_answer})

    if len(conversation_history) > 40:
        recent = conversation_history[-30:]
        conversation_history.clear()
        conversation_history.append(_system_message)
        conversation_history.extend(recent)

    _save_history()
    return final_answer


_load_history()
