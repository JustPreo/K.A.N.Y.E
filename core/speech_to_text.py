import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from core.config_loader import get_config

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        config = get_config()
        model_size = config.get("stt_whisper_model", "base")
        print(f"K.A.N.Y.E.: Cargando modelo Whisper '{model_size}'...")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model


def _record_until_silence(
    sample_rate: int = 16000,
    silence_threshold: int = 500,
    silence_secs: float = 1.5,
    max_secs: float = 10.0,
    initial_wait_secs: float = 3.0,
) -> np.ndarray:
    """
    Graba audio desde el micrófono hasta detectar silencio o alcanzar el límite.
    Espera hasta initial_wait_secs para que el usuario empiece a hablar.
    """
    chunk_size = 1024
    all_frames: list[np.ndarray] = []
    silent_chunks = 0
    speech_detected = False

    chunks_per_sec = sample_rate / chunk_size
    max_silent = int(silence_secs * chunks_per_sec)
    max_total = int(max_secs * chunks_per_sec)
    initial_wait = int(initial_wait_secs * chunks_per_sec)
    waited = 0

    with sd.InputStream(
        samplerate=sample_rate, channels=1, dtype="int16", blocksize=chunk_size
    ) as stream:
        for _ in range(max_total + initial_wait):
            data, _ = stream.read(chunk_size)
            rms = float(np.sqrt(np.mean(data.astype(np.float32) ** 2)))

            if not speech_detected:
                if rms > silence_threshold:
                    speech_detected = True
                    all_frames.append(data.copy())
                else:
                    waited += 1
                    if waited >= initial_wait:
                        break
            else:
                all_frames.append(data.copy())
                if rms < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks >= max_silent:
                        break
                else:
                    silent_chunks = 0

    if not all_frames:
        return np.array([], dtype=np.float32)

    audio = np.concatenate(all_frames, axis=0).flatten()
    return audio.astype(np.float32) / 32768.0


def listen_once(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    try:
        config = get_config()
        silence_threshold = config.get("stt_silence_threshold", 500)
        silence_secs = config.get("stt_silence_secs", 1.5)
        max_secs = config.get("stt_max_secs", 10.0)

        audio = _record_until_silence(
            silence_threshold=silence_threshold,
            silence_secs=silence_secs,
            max_secs=min(float(phrase_time_limit), max_secs),
            initial_wait_secs=float(timeout),
        )

        # Menos de 0.4 segundos de audio = nada útil
        if len(audio) < 16000 * 0.4:
            return ""

        model = _get_model()
        segments, _ = model.transcribe(
            audio,
            language=config.get("language", "es"),
            beam_size=1,
            best_of=1,
            vad_filter=True,
            vad_parameters={"threshold": 0.5},
        )

        text = " ".join(seg.text for seg in segments).strip().lower()
        return text

    except Exception as error:
        print(f"K.A.N.Y.E.: Error en STT: {error}")
        return ""
