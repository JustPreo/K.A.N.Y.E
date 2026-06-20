import shutil
import subprocess

_process: subprocess.Popen | None = None
_current_url: str | None = None
_on_change_callback = None   # fn(url_or_none)


def set_on_change(callback) -> None:
    global _on_change_callback
    _on_change_callback = callback


def play(url: str) -> bool:
    global _process, _current_url

    if not shutil.which("mpv"):
        return False

    stop()

    _process = subprocess.Popen(
        ["mpv", "--no-terminal", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _current_url = url

    if _on_change_callback:
        _on_change_callback(url)

    return True


def stop() -> None:
    global _process, _current_url

    if _process:
        try:
            _process.terminate()
        except Exception:
            pass
        _process = None

    _current_url = None

    if _on_change_callback:
        _on_change_callback(None)


def is_playing() -> bool:
    if _process is None:
        return False
    return _process.poll() is None


def current_url() -> str | None:
    return _current_url if is_playing() else None
