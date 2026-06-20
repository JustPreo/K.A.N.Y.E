"""
Modo focus: bloquea sitios distractores editando el archivo hosts.
Requiere permisos de escritura en /etc/hosts (Linux: sudo; Windows: admin).
"""
import subprocess
import sys
import threading
import time
from pathlib import Path

_MARKER_START = "# K.A.N.Y.E. FOCUS START"
_MARKER_END   = "# K.A.N.Y.E. FOCUS END"

_HOSTS_LINUX   = Path("/etc/hosts")
_HOSTS_WINDOWS = Path(r"C:\Windows\System32\drivers\etc\hosts")

_timer: threading.Timer | None = None
_active = False
_blocked_sites: list[str] = []

# Callbacks inyectados desde main.py
_on_expired_fn = None   # llamado cuando el timer termina
_speak_fn      = None
_notify_fn     = None


def set_callbacks(on_expired=None, speak=None, notify=None) -> None:
    global _on_expired_fn, _speak_fn, _notify_fn
    _on_expired_fn = on_expired
    _speak_fn      = speak
    _notify_fn     = notify


def is_active() -> bool:
    return _active


def _hosts_file() -> Path:
    return _HOSTS_WINDOWS if sys.platform == "win32" else _HOSTS_LINUX


def _write_hosts(content: str) -> bool:
    hosts = _hosts_file()
    if sys.platform == "win32":
        try:
            hosts.write_text(content, encoding="utf-8")
            return True
        except PermissionError:
            print(
                "K.A.N.Y.E.: Sin permisos para editar hosts en Windows.\n"
                "  Ejecutá K.A.N.Y.E. como administrador para usar modo focus."
            )
            return False
    else:
        result = subprocess.run(
            ["sudo", "tee", str(hosts)],
            input=content.encode("utf-8"),
            capture_output=True,
        )
        if result.returncode != 0:
            print(
                "K.A.N.Y.E.: No pude escribir en /etc/hosts.\n"
                "  Para modo focus sin contraseña, agrega esta línea a /etc/sudoers:\n"
                f"    {_get_username()} ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts"
            )
            return False
        return True


def _get_username() -> str:
    import os
    return os.environ.get("USER", os.environ.get("USERNAME", "tu_usuario"))


def _block(sites: list[str]) -> bool:
    hosts = _hosts_file()
    try:
        original = hosts.read_text(encoding="utf-8")
    except Exception as e:
        print(f"K.A.N.Y.E.: No pude leer hosts: {e}")
        return False

    if _MARKER_START in original:
        return True  # Ya bloqueado

    lines = [_MARKER_START]
    for site in sites:
        clean = site.lstrip("www.").lstrip("https://").lstrip("http://").rstrip("/")
        lines += [f"127.0.0.1\t{clean}", f"127.0.0.1\twww.{clean}"]
    lines.append(_MARKER_END)

    new_content = original.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"
    return _write_hosts(new_content)


def _unblock() -> bool:
    hosts = _hosts_file()
    try:
        original = hosts.read_text(encoding="utf-8")
    except Exception as e:
        print(f"K.A.N.Y.E.: No pude leer hosts: {e}")
        return False

    if _MARKER_START not in original:
        return True

    filtered, skip = [], False
    for line in original.splitlines():
        if line.strip() == _MARKER_START:
            skip = True
        elif line.strip() == _MARKER_END:
            skip = False
        elif not skip:
            filtered.append(line)

    return _write_hosts("\n".join(filtered).rstrip("\n") + "\n")


def _on_timer_expired() -> None:
    global _active, _timer
    _active = False
    _timer  = None

    ok = _unblock()
    msg = (
        "Tiempo de focus terminado. Sitios desbloqueados. Bien hecho."
        if ok else
        "Tiempo terminado pero no pude desbloquear los sitios. Revisá manualmente."
    )

    print(f"\nK.A.N.Y.E.: {msg}\n")
    if _notify_fn:
        _notify_fn("K.A.N.Y.E. — Focus", msg)
    if _speak_fn:
        _speak_fn(msg, use_cache=False)

    if _on_expired_fn:
        _on_expired_fn()


# ─── API pública ──────────────────────────────────────────────────────────────

def activate(sites: list[str], duration_minutes: int) -> bool:
    """Bloquea sitios e inicia el timer."""
    global _active, _timer, _blocked_sites

    if _active:
        print("K.A.N.Y.E.: Ya hay un modo focus activo.")
        return False

    if not _block(sites):
        return False

    _active        = True
    _blocked_sites = sites[:]

    _timer = threading.Timer(duration_minutes * 60, _on_timer_expired)
    _timer.daemon  = True
    _timer.start()

    print(
        f"K.A.N.Y.E.: Focus activado — {len(sites)} sitios bloqueados "
        f"por {duration_minutes} min."
    )
    return True


def deactivate(forced: bool = False) -> bool:
    """Desbloquea sitios (por el usuario o por el timer)."""
    global _active, _timer

    if _timer:
        _timer.cancel()
        _timer = None

    ok = _unblock()
    _active = False

    if ok and forced:
        print("K.A.N.Y.E.: Sitios desbloqueados manualmente.")
    return ok


def remaining_minutes() -> int:
    """Devuelve los minutos restantes del focus actual (0 si no está activo)."""
    if not _active or _timer is None:
        return 0
    # Timer no expone el tiempo restante directamente
    # Lo almacenamos al activar
    return getattr(_timer, "_remaining", 0)


def time_info() -> str:
    if not _active:
        return "No hay modo focus activo."
    return f"Focus activo. Sitios bloqueados: {', '.join(_blocked_sites)}."
