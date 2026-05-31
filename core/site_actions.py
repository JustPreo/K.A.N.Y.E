import json
import webbrowser
from pathlib import Path
from rapidfuzz import process, fuzz


SITES_FILE = Path("config") / "sites.json"


def load_sites() -> dict:
    if not SITES_FILE.exists():
        return {}

    try:
        with open(SITES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as error:
        print(f"K.A.N.Y.E.: Error leyendo sites.json: {error}")
        return {}


def find_best_site_match(query: str) -> tuple[str, str] | None:
    """
    Busca el sitio más parecido.
    Devuelve:
    - nombre del sitio
    - URL
    """
    query = query.lower().strip()
    sites = load_sites()

    if not sites:
        return None

    site_names = list(sites.keys())

    match = process.extractOne(
        query,
        site_names,
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    matched_name, score, index = match

    if score < 70:
        return None

    url = sites[matched_name]

    return matched_name, url


def open_site(query: str) -> bool:
    site = find_best_site_match(query)

    if not site:
        return False

    site_name, url = site

    print(f"K.A.N.Y.E.: Abriendo sitio: {site_name} → {url}")
    webbrowser.open(url)

    return True