import numpy as np
import sounddevice as sd


def calibrate(duration: float = 1.2, sample_rate: int = 16000, multiplier: float = 2.5) -> int:
    """
    Mide el ruido ambiente durante `duration` segundos y devuelve un threshold
    adaptado: multiplier × nivel de ruido de fondo.
    Siempre queda entre 150 y 3000.
    """
    chunk_size = 1024
    rms_values: list[float] = []

    try:
        with sd.InputStream(
            samplerate=sample_rate, channels=1, dtype="int16", blocksize=chunk_size
        ) as stream:
            chunks = int(duration * sample_rate / chunk_size)
            for _ in range(chunks):
                data, _ = stream.read(chunk_size)
                rms = float(np.sqrt(np.mean(data.astype(np.float32) ** 2)))
                rms_values.append(rms)
    except Exception as error:
        print(f"K.A.N.Y.E.: No pude calibrar el micrófono: {error}")
        return 500

    if not rms_values:
        return 500

    ambient = float(np.mean(rms_values))
    threshold = int(ambient * multiplier)
    clamped = max(150, min(threshold, 3000))

    print(f"K.A.N.Y.E.: Ruido ambiente: {ambient:.0f} → threshold: {clamped}")
    return clamped
