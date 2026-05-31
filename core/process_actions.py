import psutil
from rapidfuzz import process, fuzz
import os

def get_running_processes() -> list[dict]:
    """
    Devuelve procesos activos con nombre y PID.
    """
    processes = []

    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            name = proc.info.get("name")
            exe = proc.info.get("exe")

            if not name:
                continue

            processes.append({
                "pid": proc.info["pid"],
                "name": name,
                "exe": exe
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def close_application(query: str) -> bool:
    """
    Cierra procesos activos parecidos al nombre indicado.
    Ejemplo:
    query = "brave" -> brave.exe
    query = "whatsapp" -> WhatsApp.exe
    """
    query = query.lower().strip()

    if not query:
        return False

    processes = get_running_processes()

    if not processes:
        return False

    process_names = [proc["name"].lower() for proc in processes]

    match = process.extractOne(
        query,
        process_names,
        scorer=fuzz.WRatio
    )

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


PROTECTED_PROCESSES = [
    "python.exe",
    "pythonw.exe",
    "powershell.exe",
    "windowsterminal.exe",
    "cmd.exe",
    "explorer.exe",
    "ollama.exe",
    "ollama app.exe"
]


def close_all_desktop_apps() -> bool:
    """
    Cierra aplicaciones de escritorio evitando cerrar K.A.N.Y.E.,
    Windows Explorer, terminal, Python y Ollama.
    """
    current_pid = os.getpid()
    closed_any = False

    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            pid = proc.info["pid"]
            name = proc.info.get("name")
            exe = proc.info.get("exe") or ""

            if not name:
                continue

            name_lower = name.lower()
            exe_lower = exe.lower()

            if pid == current_pid:
                continue

            if name_lower in PROTECTED_PROCESSES:
                continue

            if "windows\\system32" in exe_lower:
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