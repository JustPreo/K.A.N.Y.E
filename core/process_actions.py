import os

import psutil
from rapidfuzz import process, fuzz

from core.platform_utils import is_windows

PROTECTED_WINDOWS = {
    "python.exe", "pythonw.exe", "powershell.exe",
    "windowsterminal.exe", "cmd.exe", "explorer.exe",
    "ollama.exe", "ollama app.exe",
}

PROTECTED_LINUX = {
    "python", "python3", "bash", "zsh", "fish", "sh",
    "gnome-shell", "plasmashell", "kwin_wayland", "kwin_x11",
    "sway", "hyprland", "i3", "openbox", "xfwm4",
    "xorg", "Xorg", "Xwayland",
    "ollama", "systemd", "init", "dbus-daemon",
}


def _get_protected() -> set[str]:
    return PROTECTED_WINDOWS if is_windows() else PROTECTED_LINUX


def _is_system_process(name: str, exe: str) -> bool:
    if is_windows():
        return "windows\\system32" in exe.lower()
    else:
        protected_paths = ("/usr/lib/systemd", "/lib/systemd", "/sbin/", "/usr/sbin/")
        return any(exe.startswith(p) for p in protected_paths)


def get_running_processes() -> list[dict]:
    processes = []

    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            name = proc.info.get("name")
            exe = proc.info.get("exe") or ""

            if not name:
                continue

            processes.append({"pid": proc.info["pid"], "name": name, "exe": exe})

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def close_application(query: str) -> bool:
    query = query.lower().strip()

    if not query:
        return False

    processes = get_running_processes()

    if not processes:
        return False

    process_names = [proc["name"].lower() for proc in processes]

    match = process.extractOne(query, process_names, scorer=fuzz.WRatio)

    if not match:
        print("K.A.N.Y.E.: No encontré un proceso parecido.")
        return False

    matched_name, score, index = match

    if score < 55:
        print(f"K.A.N.Y.E.: Coincidencia muy baja: {matched_name} | Score: {score}")
        return False

    target_name = processes[index]["name"]
    print(f"K.A.N.Y.E.: Proceso objetivo: {target_name} | Score: {score}")

    closed_any = False

    for proc in processes:
        if proc["name"].lower() == target_name.lower():
            try:
                process_obj = psutil.Process(proc["pid"])
                process_obj.terminate()
                closed_any = True
                print(f"K.A.N.Y.E.: Cerrando {proc['name']} | PID: {proc['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
                print(f"K.A.N.Y.E.: No pude cerrar {proc['name']}: {error}")

    return closed_any


def close_all_desktop_apps() -> bool:
    current_pid = os.getpid()
    protected = _get_protected()
    closed_any = False

    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            pid = proc.info["pid"]
            name = proc.info.get("name") or ""
            exe = proc.info.get("exe") or ""

            if not name:
                continue

            if pid == current_pid:
                continue

            if name.lower() in protected or name in protected:
                continue

            if exe and _is_system_process(name, exe):
                continue

            if not exe:
                continue

            process_obj = psutil.Process(pid)
            process_obj.terminate()
            print(f"K.A.N.Y.E.: Cerrando {name} | PID: {pid}")
            closed_any = True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as error:
            print(f"K.A.N.Y.E.: No pude cerrar {proc.info.get('name')}: {error}")

    return closed_any
