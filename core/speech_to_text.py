import speech_recognition as sr


def listen_once(timeout: int = 5, phrase_time_limit: int = 6) -> str:
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

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