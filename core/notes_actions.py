"""
Notas persistentes: "recordá esto" sobrevive fuera del historial de chat,
que se trunca a los últimos 24 mensajes (core/agent.py).
"""
import json
from datetime import datetime

from core.config_loader import PROJECT_ROOT

NOTES_FILE = PROJECT_ROOT / "config" / "notes.json"


def _load() -> list[dict]:
    if not NOTES_FILE.exists():
        return []
    try:
        data = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(notes: list[dict]) -> None:
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")


def add_note(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    notes = _load()
    notes.append({"text": text, "created_at": datetime.now().isoformat(timespec="seconds")})
    _save(notes)
    return True


def list_notes() -> list[dict]:
    return _load()


def search_notes(query: str) -> list[dict]:
    query = query.lower().strip()
    if not query:
        return _load()
    return [n for n in _load() if query in n["text"].lower()]


def delete_notes(query: str) -> int:
    """Borra las notas cuyo texto contiene `query`. Devuelve cuántas borró."""
    query = query.lower().strip()
    if not query:
        return 0
    notes = _load()
    kept = [n for n in notes if query not in n["text"].lower()]
    deleted = len(notes) - len(kept)
    if deleted:
        _save(kept)
    return deleted
