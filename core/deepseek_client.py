import requests

from core.config_loader import get_config

API_URL = "https://api.deepseek.com/chat/completions"


class DeepSeekError(Exception):
    pass


def is_enabled() -> bool:
    config = get_config()
    return config.get("chat_backend") == "deepseek" and bool(config.get("deepseek_api_key"))


def chat(messages: list[dict], temperature: float = 0.55, max_tokens: int = 260) -> str:
    config = get_config()
    api_key = config.get("deepseek_api_key")
    model = config.get("deepseek_model", "deepseek-chat")

    if not api_key:
        raise DeepSeekError("Falta deepseek_api_key en config.local.json")

    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as error:
        raise DeepSeekError(str(error)) from error
    except (KeyError, IndexError, ValueError) as error:
        raise DeepSeekError(f"Respuesta inesperada de DeepSeek: {error}") from error


def chat_with_tools(
    messages: list[dict],
    tools: list[dict],
    temperature: float = 0.4,
    max_tokens: int = 300,
) -> dict:
    """Como chat(), pero manda `tools` (formato OpenAI-compatible) y devuelve
    el mensaje completo del modelo (content + tool_calls), no solo el texto,
    para que el loop del agente pueda decidir qué hacer con los tool_calls."""
    config = get_config()
    api_key = config.get("deepseek_api_key")
    model = config.get("deepseek_model", "deepseek-chat")

    if not api_key:
        raise DeepSeekError("Falta deepseek_api_key en config.local.json")

    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "tools": tools,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        message = data["choices"][0]["message"]
        return {
            "role": "assistant",
            "content": message.get("content") or "",
            "tool_calls": message.get("tool_calls") or None,
        }
    except requests.RequestException as error:
        raise DeepSeekError(str(error)) from error
    except (KeyError, IndexError, ValueError) as error:
        raise DeepSeekError(f"Respuesta inesperada de DeepSeek: {error}") from error
