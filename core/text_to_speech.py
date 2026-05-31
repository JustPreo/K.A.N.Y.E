import hashlib
import subprocess
import tempfile
from pathlib import Path

import sounddevice as sd
import soundfile as sf


VOICE_MODEL = Path("voices") / "es_ES-davefx-medium.onnx"
CACHE_DIR = Path("cache") / "tts"
TEMP_WAV = Path(tempfile.gettempdir()) / "kanye_temp_response.wav"


def get_cache_path(text: str) -> Path:
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{text_hash}.wav"


def play_wav(wav_path: Path) -> None:
    data, sample_rate = sf.read(str(wav_path), dtype="float32")
    sd.play(data, sample_rate)
    sd.wait()


def generate_with_piper(text: str, output_path: Path) -> bool:
    if not VOICE_MODEL.exists():
        print(f"K.A.N.Y.E.: No encontré la voz Piper en: {VOICE_MODEL}")
        return False

    try:
        command = [
            "piper",
            "--model",
            str(VOICE_MODEL),
            "--output_file",
            str(output_path)
        ]

        subprocess.run(
            command,
            input=text,
            text=True,
            check=True,
            capture_output=True
        )

        return True

    except Exception as error:
        print(f"K.A.N.Y.E.: Error usando Piper: {error}")
        return False


def speak(text: str, use_cache: bool = True) -> None:
    if not text:
        return

    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        wav_path = get_cache_path(text)

        if not wav_path.exists():
            generated = generate_with_piper(text, wav_path)

            if not generated:
                return

        play_wav(wav_path)
        return

    generated = generate_with_piper(text, TEMP_WAV)

    if generated:
        play_wav(TEMP_WAV)