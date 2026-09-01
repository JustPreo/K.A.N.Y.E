import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

_config_cache: dict | None = None


def get_config() -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_path = PROJECT_ROOT / "config" / "config.json"

    defaults = {
        "hotkey": "ctrl+f9",
        "stt_backend": "whisper",
        "stt_whisper_model": "base",
        "stt_silence_threshold": 500,
        "stt_silence_secs": 1.5,
        "stt_max_secs": 10.0,
        "chat_model": "phi4-mini",
        "chat_backend": "ollama",
        "max_tool_iterations": 6,
        "deepseek_model": "deepseek-chat",
        "deepseek_api_key": "",
        "voice_model": "voices/es_ES-davefx-medium.onnx",
        "tts_cache_dir": "cache/tts",
        "language": "es",
        "startup_tts": True,
        "auto_listen_on_hotkey": True,
        "it_worker_max_steps": 8,
        "it_worker_model": "deepseek-v4-flash-vision-exp",
    }

    if not config_path.exists():
        _config_cache = defaults
        return _config_cache

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        _config_cache = {**defaults, **loaded}
    except Exception as error:
        print(f"K.A.N.Y.E.: Error leyendo config.json: {error}. Usando defaults.")
        _config_cache = defaults

    local_path = PROJECT_ROOT / "config" / "config.local.json"
    if local_path.exists():
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                local = json.load(f)
            _config_cache = {**_config_cache, **local}
        except Exception as error:
            print(f"K.A.N.Y.E.: Error leyendo config.local.json: {error}. Ignorando.")

    return _config_cache
