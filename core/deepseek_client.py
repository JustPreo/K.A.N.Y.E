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
