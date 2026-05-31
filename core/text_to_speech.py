import pyttsx3


def speak(text: str) -> None:
    if not text:
        return

    try:
        engine = pyttsx3.init("sapi5")
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as error:
        print(f"K.A.N.Y.E.: Error de voz: {error}")