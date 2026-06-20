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
        "intent_model": "qwen2.5:1.5b",
        "use_llm_classifier": True,
        "voice_model": "voices/es_ES-davefx-medium.onnx",
        "tts_cache_dir": "cache/tts",
        "language": "es",
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

    return _config_cache
