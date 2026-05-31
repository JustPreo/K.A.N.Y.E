import pyttsx3


engine = pyttsx3.init()


def setup_voice() -> None:
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)


def speak(text: str) -> None:
    if not text:
        return

    setup_voice()
    engine.say(text)
    engine.runAndWait()