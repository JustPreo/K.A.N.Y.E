import speech_recognition as sr


def listen_once(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    recognizer = sr.Recognizer()

    # Cuánto silencio permite antes de decidir que terminaste de hablar.
    recognizer.pause_threshold = 1.4

    # Hace que no corte tan agresivo.
    recognizer.non_speaking_duration = 0.6

    # Ajuste de ruido. Más bajo para que no tarde tanto.
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio, language="es-HN")
        return text.lower().strip()

    except sr.UnknownValueError:
        return ""

    except sr.RequestError:
        print("K.A.N.Y.E.: Error con el reconocimiento de voz.")
        return ""

    except Exception as error:
        print(f"K.A.N.Y.E.: Error inesperado en voz: {error}")
        return ""