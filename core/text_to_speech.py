import subprocess
import tempfile
from pathlib import Path
import sounddevice as sd
import soundfile as sf


VOICE_MODEL = Path("voices") / "es_ES-davefx-medium.onnx"
OUTPUT_WAV = Path(tempfile.gettempdir()) / "kanye_piper_response.wav"


def speak(text: str) -> None:
    if not text:
        return

    if not VOICE_MODEL.exists():
        print(f"K.A.N.Y.E.: No encontré la voz Piper en: {VOICE_MODEL}")
        return

    try:
        command = [
            "piper",
            "--model",
            str(VOICE_MODEL),
            "--output_file",
            str(OUTPUT_WAV)
        ]

        subprocess.run(
            command,
            input=text,
            text=True,
            check=True,
            capture_output=True
        )

        data, sample_rate = sf.read(str(OUTPUT_WAV), dtype="float32")
        sd.play(data, sample_rate)
        sd.wait()

    except Exception as error:
        print(f"K.A.N.Y.E.: Error usando Piper: {error}")