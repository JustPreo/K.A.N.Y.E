import hashlib
import io
import tempfile
import wave
from pathlib import Path

import sounddevice as sd
import soundfile as sf

from core.config_loader import get_config, PROJECT_ROOT

_voice = None


def _get_voice():
    global _voice
    if _voice is None:
        try:
            from piper.voice import PiperVoice
        except ImportError:
            raise RuntimeError(
                "piper-tts no está instalado. Ejecutá: pip install piper-tts"
            )

        config = get_config()
        model_rel = config.get("voice_model", "voices/es_ES-davefx-medium.onnx")
        model_path = PROJECT_ROOT / model_rel

        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo de voz no encontrado: {model_path}\n"
                "Descargalo de: https://huggingface.co/rhasspy/piper-voices"
            )

        _voice = PiperVoice.load(str(model_path))
    return _voice


def _get_cache_dir() -> Path:
    config = get_config()
    cache_dir = PROJECT_ROOT / config.get("tts_cache_dir", "cache/tts")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_cache_path(text: str) -> Path:
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    return _get_cache_dir() / f"{text_hash}.wav"


def _synthesize_to_wav(text: str, wav_path: Path) -> bool:
    try:
        voice = _get_voice()
        with wave.open(str(wav_path), "wb") as wav_file:
            voice.synthesize(text, wav_file)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error sintetizando voz: {error}")
        return False


def _play_wav(wav_path: Path) -> None:
    data, sample_rate = sf.read(str(wav_path), dtype="float32")
    sd.play(data, sample_rate)
    sd.wait()


def speak(text: str, use_cache: bool = True) -> None:
    if not text:
        return

    if use_cache:
        wav_path = _get_cache_path(text)
        if not wav_path.exists():
            if not _synthesize_to_wav(text, wav_path):
                return
        _play_wav(wav_path)
        return

    temp_wav = Path(tempfile.gettempdir()) / "kanye_temp_response.wav"
    if _synthesize_to_wav(text, temp_wav):
        _play_wav(temp_wav)
