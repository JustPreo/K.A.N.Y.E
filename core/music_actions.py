import subprocess
import webbrowser
from urllib.parse import quote_plus


def search_youtube_first_video(query: str) -> str | None:
    """
    Busca el primer resultado de YouTube usando yt-dlp.
    Devuelve el ID del video si lo encuentra.
    """
    if not query:
        return None

    try:
        command = [
            "python",
            "-m",
            "yt_dlp",
            f"ytsearch1:{query}",
            "--print",
            "%(id)s",
            "--no-playlist",
            "--skip-download",
            "--no-warnings"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=25
        )

        lines = result.stdout.strip().splitlines()

        if not lines:
            print("K.A.N.Y.E.: yt-dlp no devolvió resultados.")
            if result.stderr:
                print(result.stderr)
            return None

        video_id = lines[0].strip()

        if not video_id:
            return None

        return video_id

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