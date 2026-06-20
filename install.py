#!/usr/bin/env python3
"""
K.A.N.Y.E. Installer — Cross-platform (Windows / Linux)
Ejecutar con: python install.py
"""
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VENV_DIR = PROJECT_ROOT / ".venv"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"  → {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, **kwargs)


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def venv_python() -> str:
    if is_windows():
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python3")


def venv_pip() -> str:
    if is_windows():
        return str(VENV_DIR / "Scripts" / "pip.exe")
    return str(VENV_DIR / "bin" / "pip")


def step_create_venv():
    print("\n[0/6] Configurando entorno virtual...")
    if VENV_DIR.exists():
        print("  ✓ Entorno virtual ya existe (.venv/)")
        return
    result = run([sys.executable, "-m", "venv", str(VENV_DIR)])
    if result.returncode != 0:
        print("  ✗ No pude crear el entorno virtual.")
        sys.exit(1)
    print("  ✓ Entorno virtual creado en .venv/")


def detect_linux_distro() -> str:
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.split("=", 1)[1].strip().strip('"').lower()
    except Exception:
        pass
    return "unknown"


# ─── Pasos ────────────────────────────────────────────────────────────────────

def step_python_deps():
    print("\n[1/6] Instalando dependencias Python...")
    reqs = PROJECT_ROOT / "requirements.txt"
    result = run(
        [venv_pip(), "install", "-r", str(reqs)],
        capture_output=False,
    )
    if result.returncode != 0:
        print("  ✗ Falló la instalación de dependencias Python.")
        sys.exit(1)
    print("  ✓ Dependencias Python instaladas.")


def step_system_deps_linux():
    print("\n[2/6] Instalando dependencias del sistema (Linux)...")

    distro = detect_linux_distro()
    print(f"  Distro detectada: {distro}")

    # Paquetes requeridos por grupo
    # portaudio: sounddevice | playerctl: control multimedia | pactl: volumen
    ubuntu_pkgs = ["portaudio19-dev", "libsndfile1", "playerctl", "pulseaudio-utils"]
    fedora_pkgs = ["portaudio-devel", "libsndfile-devel", "playerctl", "pulseaudio-utils"]
    arch_pkgs   = ["portaudio", "libsndfile", "playerctl", "libpulse"]

    if distro in ("ubuntu", "debian", "linuxmint", "pop", "elementary", "zorin"):
        run(["sudo", "apt-get", "update", "-qq"])
        run(["sudo", "apt-get", "install", "-y"] + ubuntu_pkgs)
    elif distro in ("fedora",):
        run(["sudo", "dnf", "install", "-y"] + fedora_pkgs)
    elif distro in ("rhel", "centos", "almalinux", "rocky"):
        run(["sudo", "dnf", "install", "-y"] + fedora_pkgs)
    elif distro in ("arch", "manjaro", "endeavouros", "garuda"):
        run(["sudo", "pacman", "-S", "--noconfirm"] + arch_pkgs)
    elif distro in ("opensuse", "opensuse-leap", "opensuse-tumbleweed"):
        run(["sudo", "zypper", "install", "-y", "portaudio-devel", "playerctl"])
    else:
        print(
            "  ! Distro no reconocida. Instalá manualmente:\n"
            "    portaudio, libsndfile, playerctl, pulseaudio-utils"
        )

    print("  ✓ Dependencias de sistema procesadas.")


def step_check_ollama():
    print("\n[3/6] Verificando Ollama...")

    result = run(["ollama", "list"], capture_output=True, text=True)

    if result.returncode != 0:
        print("  ✗ Ollama no está instalado.")
        if is_linux():
            print("  → Instalando Ollama...")
            install_result = subprocess.run(
                "curl -fsSL https://ollama.com/install.sh | sh",
                shell=True,
            )
            if install_result.returncode != 0:
                print(
                    "  ✗ No pude instalar Ollama automáticamente.\n"
                    "    Instalalo manualmente: https://ollama.com/download"
                )
                return
        else:
            print("  → Descargá e instalá Ollama desde: https://ollama.com/download")
            print("  → Luego volvé a ejecutar install.py")
            return

    print("  ✓ Ollama disponible.")
    print("\n  Descargando modelos (puede tardar según tu conexión)...")

    print("  → phi4-mini (chat, ~2.5 GB)...")
    run(["ollama", "pull", "phi4-mini"])

    print("  → qwen2.5:1.5b (clasificador, ~1 GB)...")
    run(["ollama", "pull", "qwen2.5:1.5b"])

    print("  ✓ Modelos Ollama listos.")


def step_check_voice_model():
    print("\n[4/6] Verificando modelo de voz Piper...")

    onnx = PROJECT_ROOT / "voices" / "es_ES-davefx-medium.onnx"
    json_cfg = PROJECT_ROOT / "voices" / "es_ES-davefx-medium.onnx.json"

    if onnx.exists() and json_cfg.exists():
        print("  ✓ Modelo de voz encontrado.")
        return

    (PROJECT_ROOT / "voices").mkdir(exist_ok=True)

    print("  ! Modelo de voz no encontrado.")
    print("  → Descargando es_ES-davefx-medium...")

    base_url = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
        "es/es_ES/davefx/medium"
    )

    for fname in ["es_ES-davefx-medium.onnx", "es_ES-davefx-medium.onnx.json"]:
        dest = PROJECT_ROOT / "voices" / fname
        print(f"  → {fname}")
        result = subprocess.run(
            ["curl", "-L", "--progress-bar", f"{base_url}/{fname}", "-o", str(dest)],
            capture_output=False,
        )
        if result.returncode != 0:
            print(
                f"  ✗ No pude descargar {fname}.\n"
                f"    Descargalo manualmente de:\n    {base_url}/{fname}\n"
                f"    y colocalo en voices/"
            )
            return

    print("  ✓ Modelo de voz descargado.")


def step_download_whisper():
    print("\n[5/6] Descargando modelo Whisper (base, ~74 MB)...")
    result = run(
        [venv_python(), "-c",
         "from faster_whisper import WhisperModel; "
         "WhisperModel('base', device='cpu', compute_type='int8'); "
         "print('  ✓ Modelo Whisper listo.')"],
        capture_output=False,
    )
    if result.returncode != 0:
        print("  ✗ Error descargando Whisper. Intentalo manualmente después.")


def step_post_install_notes():
    print("\n[6/6] Notas finales...")

    if is_linux():
        print(
            "\n  IMPORTANTE — Hotkey global en Linux:\n"
            "  Si el hotkey (Ctrl+F9) no responde, agrega tu usuario al grupo 'input':\n"
            "    sudo usermod -aG input $USER\n"
            "  Luego cierra sesión y vuelve a entrar.\n"
            "\n  Si usás Wayland y el hotkey sigue sin responder:\n"
            "    1. Ejecutá K.A.N.Y.E. con: sudo python main.py\n"
            "    2. O cambiá a sesión X11\n"
            "    3. O el asistente activará modo terminal (presioná Enter)\n"
            "\n  OPCIONAL — Focus mode sin contraseña (bloqueo de sitios distractores):\n"
            "  Si querés usar 'activa modo estudio' sin que pida contraseña sudo,\n"
            "  ejecutá: sudo visudo\n"
            "  Y agregá esta línea (reemplazá TU_USUARIO con tu usuario real):\n"
            "    TU_USUARIO ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts"
        )

    print(
        "\n  RAM mínima recomendada por configuración:\n"
        "    4-6 GB  → Cambiá chat_model a 'qwen2.5:1.5b' en config/config.local.json\n"
        "              y use_llm_classifier a false\n"
        "    8 GB    → Configuración actual (phi4-mini + qwen2.5:1.5b)\n"
        "    16 GB+  → Podés subir a modelos más grandes si querés\n"
        "\n  Whisper model vs velocidad:\n"
        "    tiny  (~39 MB)  → ultra rápido, menos preciso\n"
        "    base  (~74 MB)  → balance ideal (default)\n"
        "    small (~244 MB) → más preciso, más lento\n"
        "  Cambialo en config/config.local.json → stt_whisper_model\n"
        "\n  Archivos personales (no están en git, son tuyos):\n"
        "    config/modes.json       → tus modos de trabajo\n"
        "    config/sites.json       → tus sitios guardados\n"
        "    config/config.local.json → tus overrides de config"
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  K.A.N.Y.E. Installer")
    print(f"  Sistema: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python:  {sys.version.split()[0]}")
    print("=" * 55)

    step_create_venv()
    step_python_deps()

    if is_linux():
        step_system_deps_linux()
    else:
        print("\n[2/6] Dependencias del sistema: no requeridas en Windows. ✓")

    step_check_ollama()
    step_check_voice_model()
    step_download_whisper()
    step_post_install_notes()

    print("\n" + "=" * 55)
    print("  Instalación completa.")
    if is_windows():
        print("  Iniciá el asistente con:")
        print("    .venv\\Scripts\\activate")
        print("    python main.py")
    else:
        print("  Iniciá el asistente con:")
        print("    source .venv/bin/activate")
        print("    python3 main.py")
        print()
        print("  O sin activar el venv:")
        print("    .venv/bin/python3 main.py")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
