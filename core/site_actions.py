import json
import re
import webbrowser
from pathlib import Path

from rapidfuzz import process, fuzz

SITES_FILE = Path("config") / "sites.json"


def load_sites() -> dict:
    if not SITES_FILE.exists():
        return {}
    try:
        with open(SITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        print(f"K.A.N.Y.E.: Error leyendo sites.json: {error}")
        return {}


def _save_sites(sites: dict) -> bool:
    try:
        SITES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SITES_FILE, "w", encoding="utf-8") as f:
            json.dump(sites, f, indent=4, ensure_ascii=False)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error guardando sites.json: {error}")
        return False


def _normalize_url(text: str) -> str:
    """Normaliza una URL dictada por voz."""
    text = text.strip().lower()

    # Correcciones de STT comunes para URLs
    replacements = {
        " punto ": ".", " dot ": ".", " .": ".",
        " barra ": "/", " slash ": "/",
        " guión ": "-", " guion ": "-", " dash ": "-",
        "https dos puntos doble barra ": "https://",
        "https dos puntos barra barra ": "https://",
        "http dos puntos barra barra ": "http://",
        "https ": "https://",
        "http ": "http://",
        "www punto": "www.",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)

    # Limpia espacios sobrantes
    text = re.sub(r"\s+", "", text)

    if not text.startswith(("http://", "https://")):
        text = "https://" + text

    return text


def find_best_site_match(query: str) -> tuple[str, str] | None:
    query = query.lower().strip()
    sites = load_sites()

    if not sites:
        return None

    site_names = list(sites.keys())
    match = process.extractOne(query, site_names, scorer=fuzz.WRatio)

    if not match:
        return None

    matched_name, score, index = match
    if score < 70:
        return None

    return matched_name, sites[matched_name]


def open_site(query: str) -> bool:
    site = find_best_site_match(query)
    if not site:
        return False
    site_name, url = site
    print(f"K.A.N.Y.E.: Abriendo sitio: {site_name} → {url}")
    webbrowser.open(url)
    return True


def add_site(name: str, url_raw: str) -> bool:
    """Guarda un nuevo sitio en sites.json."""
    name = name.lower().strip()
    url = _normalize_url(url_raw)

    if not name or not url:
        return False

    sites = load_sites()
    sites[name] = url
    saved = _save_sites(sites)

    if saved:
        print(f"K.A.N.Y.E.: Sitio guardado → '{name}': {url}")

    return saved
