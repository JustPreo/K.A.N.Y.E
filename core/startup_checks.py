import sounddevice as sd

from core.config_loader import get_config, PROJECT_ROOT


def _check_voice_model() -> bool:
    config = get_config()
    model_path = PROJECT_ROOT / config.get("voice_model", "voices/es_ES-davefx-medium.onnx")

    if not model_path.exists():
        print(
            f"K.A.N.Y.E.: ✗ Modelo de voz no encontrado: {model_path}\n"
            "  Ejecutá: python install.py"
        )
        return False

    print("K.A.N.Y.E.: ✓ Modelo de voz OK")
    return True


def _check_ollama() -> bool:
    config = get_config()

    try:
        import ollama

        response = ollama.list()
        available = {m.model for m in response.models}

        needed: set[str] = {config.get("chat_model", "phi4-mini")}
        if config.get("use_llm_classifier", True):
            needed.add(config.get("intent_model", "qwen2.5:1.5b"))

        # ollama list muestra "phi4-mini:latest" pero el config dice "phi4-mini"
        def is_available(model_name: str) -> bool:
            return any(
                a == model_name or a.startswith(model_name + ":")
                for a in available
            )

        missing = {m for m in needed if not is_available(m)}

        if missing:
            print(
                f"K.A.N.Y.E.: ✗ Modelos Ollama faltantes: {missing}\n"
                f"  Ejecutá: ollama pull {' && ollama pull '.join(missing)}"
            )
            return False

        print("K.A.N.Y.E.: ✓ Ollama y modelos OK")
        return True

    except Exception as error:
        print(
            f"K.A.N.Y.E.: ✗ Ollama no responde: {error}\n"
            "  Asegurate de que Ollama esté corriendo antes de iniciar K.A.N.Y.E."
        )
        return False


def _check_microphone() -> bool:
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d["max_input_channels"] > 0]

        if not input_devices:
            print("K.A.N.Y.E.: ✗ No se detectó micrófono.")
            return False

        print(f"K.A.N.Y.E.: ✓ Micrófono OK ({input_devices[0]['name']})")
        return True

    except Exception as error:
        print(f"K.A.N.Y.E.: ✗ Error verificando micrófono: {error}")
        return False


def run_checks(abort_on_fail: bool = False) -> bool:
    """
    Verifica voz, Ollama y micrófono al arrancar.
    Si abort_on_fail=True, retorna False si algo falla.
    """
    print("K.A.N.Y.E.: Verificando sistema...")

    results = [
        _check_voice_model(),
        _check_ollama(),
        _check_microphone(),
    ]

    ok = all(results)

    if not ok:
        print(
            "\nK.A.N.Y.E.: Algunos componentes no están listos.\n"
            "  El asistente puede funcionar con limitaciones."
        )
    else:
        print("K.A.N.Y.E.: Sistema listo.\n")

    return ok
