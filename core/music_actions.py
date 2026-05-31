import re
import subprocess
import sys
import webbrowser
from urllib.parse import quote_plus


YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def extract_video_id(output: str) -> str | None:
    """
    Busca un ID válido de YouTube dentro del texto devuelto por yt-dlp.
    """
    if not output:
        return None

    lines = output.strip().splitlines()

    for line in lines:
        clean_line = line.strip()

        if YOUTUBE_ID_PATTERN.match(clean_line):
            return clean_line

    return None


def search_youtube_first_video(query: str) -> str | None:
    """
    Busca el primer resultado de YouTube usando yt-dlp.
    Devuelve el ID del video si lo encuentra.
    """
    if not query:
        return None

    try:
        command = [
            sys.executable,
            "-m",
            "yt_dlp",
            f"ytsearch1:{query}",
            "--print",
            "%(id)s",
            "--no-playlist",
            "--skip-download"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )

        combined_output = f"{result.stdout}\n{result.stderr}"

        video_id = extract_video_id(combined_output)

        if video_id:
            print(f"K.A.N.Y.E.: ID encontrado: {video_id}")
            return video_id

        print("K.A.N.Y.E.: yt-dlp no devolvió un ID válido.")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        return None

    except subprocess.TimeoutExpired:
        print("K.A.N.Y.E.: La búsqueda tardó demasiado.")
        return None

    except Exception as error:
        print(f"K.A.N.Y.E.: Error buscando canción: {error}")
        return None


def play_on_youtube_music(query: str) -> bool:
    """
    Busca el primer resultado y abre directamente YouTube Music.
    Si falla, abre la búsqueda normal.
    """
    if not query:
        return False

    video_id = search_youtube_first_video(query)

    if video_id:
        url = f"https://music.youtube.com/watch?v={video_id}"
        webbrowser.open(url)
        return True

    encoded_query = quote_plus(query)
    fallback_url = f"https://music.youtube.com/search?q={encoded_query}"
    webbrowser.open(fallback_url)
    return True