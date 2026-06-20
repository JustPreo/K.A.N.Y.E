import sys
import threading
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from core.config_loader import get_config

_model: WhisperModel | None = None
_calibrated_threshold: int | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        config = get_config()
        model_size = config.get("stt_whisper_model", "base")
        print(f"K.A.N.Y.E.: Cargando modelo Whisper '{model_size}'...")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model


def set_calibrated_threshold(threshold: int) -> None:
    global _calibrated_threshold
    _calibrated_threshold = threshold


def _get_threshold() -> int:
    if _calibrated_threshold is not None:
        return _calibrated_threshold
    config = get_config()
    return config.get("stt_silence_threshold", 500)


# ─── Indicador visual en terminal ────────────────────────────────────────────

_stop_indicator = threading.Event()


def _run_indicator() -> None:
    frames = ["⏺ GRABANDO   ", "⏺ GRABANDO.  ", "⏺ GRABANDO.. ", "⏺ GRABANDO..."]
    i = 0
    while not _stop_indicator.is_set():
        sys.stdout.write(f"\r  {frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.35)
        i += 1
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()


def _start_indicator() -> threading.Thread:
    _stop_indicator.clear()
    t = threading.Thread(target=_run_indicator, daemon=True)
    t.start()
    return t


def _stop_indicator_thread(t: threading.Thread) -> None:
    _stop_indicator.set()
    t.join(timeout=1)


# ─── Grabación con detección de silencio ─────────────────────────────────────

def _record_until_silence(
    sample_rate: int = 16000,
    silence_threshold: int = 500,
    silence_secs: float = 1.5,
    max_secs: float = 10.0,
    initial_wait_secs: float = 3.0,
) -> np.ndarray:
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


# ─── API pública ─────────────────────────────────────────────────────────────

def listen_once(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    config = get_config()
    silence_threshold = _get_threshold()
    silence_secs = config.get("stt_silence_secs", 1.5)
    max_secs = config.get("stt_max_secs", 10.0)

    indicator = _start_indicator()

    try:
        audio = _record_until_silence(
            silence_threshold=silence_threshold,
            silence_secs=silence_secs,
            max_secs=min(float(phrase_time_limit), max_secs),
            initial_wait_secs=float(timeout),
        )
    finally:
        _stop_indicator_thread(indicator)

    # Menos de 0.4s de audio = nada útil
    if len(audio) < 16000 * 0.4:
        return ""

    try:
        model = _get_model()
        segments, _ = model.transcribe(
            audio,
            language=config.get("language", "es"),
            beam_size=1,
            best_of=1,
            vad_filter=True,
            vad_parameters={"threshold": 0.5},
        )
        return " ".join(seg.text for seg in segments).strip().lower()

    except Exception as error:
        print(f"K.A.N.Y.E.: Error en STT: {error}")
        return ""
