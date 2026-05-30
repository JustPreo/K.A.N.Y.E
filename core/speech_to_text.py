import speech_recognition as sr


def listen_once() -> str:
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("K.A.N.Y.E.: Ajustando ruido ambiente...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

        print("K.A.N.Y.E.: Hablá ahora.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

    try:
        text = recognizer.recognize_google(audio, language="es-HN")
        return text.lower().strip()

    except sr.UnknownValueError:
        print("K.A.N.Y.E.: No entendí lo que dijiste.")
        return ""

    except sr.RequestError:
        print("K.A.N.Y.E.: Error con el reconocimiento de voz.")
        return ""

    except Exception as error:
        print(f"K.A.N.Y.E.: Error inesperado en voz: {error}")
        return ""