# K.A.N.Y.E.
**K**nowledge **A**ssistant **N**avigating **Y**our **E**nvironment

Asistente de voz personal, 100% local, en español. Presioná `Ctrl+F9`, hablá, y ejecuta tu comando. Sin internet para voz ni IA — todo corre en tu máquina.

**Soporta:** Linux (Ubuntu/Fedora/Arch/openSUSE) · Windows 10/11

---

## Instalación

**Requisitos:** Python 3.10+, 4 GB RAM mínimo, micrófono

```bash
git clone https://github.com/TU_USUARIO/K.A.N.Y.E.git
cd K.A.N.Y.E

# Crear tus archivos personales a partir de las plantillas
cp config/modes.example.json config/modes.json
cp config/sites.example.json config/sites.json

# Instalar todo automáticamente
python install.py

python main.py
```

`install.py` instala dependencias, Ollama, modelos de IA (`phi4-mini`, `qwen2.5:1.5b`) y el modelo de voz Piper.

<details>
<summary>Instalación manual</summary>

```bash
pip install -r requirements.txt
```

**Linux — dependencias del sistema:**
```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev libsndfile1 playerctl pulseaudio-utils

# Fedora
sudo dnf install portaudio-devel libsndfile-devel playerctl pulseaudio-utils

# Arch
sudo pacman -S portaudio libsndfile playerctl libpulse
```

**Ollama:**
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi4-mini
ollama pull qwen2.5:1.5b
```
Windows: instalador en [ollama.com/download](https://ollama.com/download)

**Modelo de voz (Piper):**
```bash
mkdir -p voices
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx" -o voices/es_ES-davefx-medium.onnx
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json" -o voices/es_ES-davefx-medium.onnx.json
```

</details>

---

## Configuración

`config/config.json` tiene los valores por defecto. Para sobreescribir sin tocar el repo, creá `config/config.local.json` (gitignore) con solo las claves que querés cambiar:

```json
{
  "hotkey": "ctrl+f9",
  "chat_model": "phi4-mini",
  "stt_whisper_model": "base",
  "max_tool_iterations": 6,
  "language": "es"
}
```

K.A.N.Y.E. es **agéntico**: `chat_model` no es solo para conversar, es el
modelo que decide qué acciones ejecutar (tool calling) y en qué orden. Por
eso necesita soportar function calling de forma confiable, no solo generar
texto:

**Por RAM disponible:**

| RAM | `chat_model` | `stt_whisper_model` | Notas |
|---|---|---|---|
| 6–8 GB | `phi4-mini` (default) | `base` | Soporte de tools limitado — para acciones simples anda bien, para cadenas largas conviene DeepSeek |
| 16 GB+ | `qwen2.5:7b` | `base` | Tool calling mucho más confiable en local |

`max_tool_iterations` limita cuántos pasos seguidos puede encadenar el
agente antes de forzarlo a responder (default 6).

---

## DeepSeek (opcional, en la nube)

Por defecto K.A.N.Y.E. usa Ollama local para chat y clasificación de intención. Si querés respuestas de más calidad y tenés API key de DeepSeek, podés activarlo en `config/config.local.json`:

```json
{
  "chat_backend": "deepseek",
  "deepseek_api_key": "sk-...",
  "deepseek_model": "deepseek-chat"
}
```

- Es el backend principal del loop agéntico (`core/agent.py`) cuando está habilitado — tool calling incluido.
- Si la llamada falla (sin internet, error de API, key inválida), cae automáticamente al modelo local de Ollama — nunca te deja sin asistente.
- `deepseek-chat` es el modelo más barato (fracciones de centavo por sesión de uso normal). No pongas la key en `config.json` (ese sí va a git); `config.local.json` está en `.gitignore`.

---

## Archivos personales

Estos archivos **no están en el repo** (`.gitignore`) porque contienen tus datos:

| Archivo | Descripción |
|---|---|
| `config/config.local.json` | Tus overrides de configuración |
| `config/modes.json` | Tus modos de trabajo |
| `config/sites.json` | Tus sitios guardados |
| `config/workspaces.json` | Tus rutas de proyectos |
| `config/history.json` | Historial de conversación |

Las plantillas `modes.example.json` y `sites.example.json` están en el repo como referencia.

---

## Cómo funciona (agéntico)

K.A.N.Y.E. **no** tiene una lista fija de frases-comando. Todo lo que decís
(después de `Ctrl+F9`) va a un loop agéntico (`core/agent.py`): el LLM
configurado (DeepSeek o el modelo local de Ollama) decide, en lenguaje
natural, qué herramientas ejecutar, en qué orden, y cuándo ya tiene una
respuesta final — sin pasar por un clasificador de intención rígido.

Podés pedir varias cosas en la misma frase y el agente las encadena solo:

```
cerrá spotify, abrí firefox y buscame el clima
activá modo estudio y bajale al volumen
```

**Herramientas disponibles** (`core/tools.py`):

| Categoría | Herramientas |
|---|---|
| Apps y sistema | `open_app`, `close_app`, `open_folder` |
| Web y búsqueda | `web_search`, `open_site`, `add_site` |
| Música y multimedia | `play_music`, `media_control` (play/pause, siguiente, anterior, volumen) |
| Teclado | `type_text`, `keyboard_shortcut` (copiar/pegar/deshacer/atajos de ventana/etc.) |
| Modos de trabajo | `activate_mode`, `list_modes` |
| Archivos de proyecto | `read_file`, `search_in_file`, `backup_file`, `replace_in_file` |
| Focus | `focus_status`, `focus_off` |

`replace_in_file` sigue pidiendo confirmación por terminal y hace backup
automático antes de tocar el archivo, igual que antes.

**Fuera del loop agéntico** (housekeeping instantáneo o wizards interactivos
que no encajan en un solo tool call, resueltos directo en `main.py` sin
pasar por el LLM):

| Di... | Acción |
|---|---|
| `salir` | Cerrar K.A.N.Y.E. |
| `borra historial` | Limpiar contexto de conversación |
| `crea modo [nombre]` | Crear modo (wizard interactivo en terminal) |
| `edita modo [nombre]` | Editar modo existente (wizard) |
| `elimina modo [nombre]` | Eliminar modo (con confirmación) |

Todo lo demás — preguntas, opiniones, y cualquier pedido de acción —
lo maneja el agente.

---

## Modos de trabajo

Guardados en `config/modes.json` (personal, no en git). Copiá la plantilla al clonar:
```bash
cp config/modes.example.json config/modes.json
```

Formato:
```json
{
    "estudio": {
        "close_before": false,
        "apps": [],
        "urls": [],
        "folders": [],
        "message": "Modo estudio. Sin distracciones.",
        "focus": {
            "enabled": true,
            "duration_minutes": 50,
            "blocked_sites": ["youtube.com", "twitter.com", "instagram.com", "reddit.com"]
        }
    }
}
```

La clave `focus` es opcional. Si está, bloquea los sitios en `/etc/hosts` por el tiempo indicado y los desbloquea automáticamente.

**Linux — sudo sin contraseña para focus:**
```bash
sudo visudo
# Agregar:
TU_USUARIO ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts
```

---

## Presencia ambiental

K.A.N.Y.E. corre dos hilos de fondo:

- **Ambient:** notificaciones motivacionales generadas por LLM a los 30, 60, 90, 120, 180 y 240 min de uso
- **Monitor:** alerta con voz + notificación si CPU > 85% por 60 seg, RAM > 90%, o batería < 15%

---

## Hotkey en Linux — Problemas

**No responde:**
```bash
sudo usermod -aG input $USER  # cerrar sesión y volver a entrar
```

**Wayland:** `pynput` tiene soporte limitado. Usá sesión X11, o K.A.N.Y.E. cae automáticamente a modo terminal (presioná Enter para activar).

**Conflicto con otra app:** cambiá el hotkey en `config/config.local.json`:
```json
{ "hotkey": "ctrl+shift+k" }
```

---

## Estructura

```
K.A.N.Y.E/
├── main.py / install.py / requirements.txt
├── config/
│   ├── config.json            # defaults (en git)
│   ├── config.local.json      # tus overrides (gitignore)
│   ├── modes.example.json     # plantilla (en git)
│   ├── modes.json             # tus modos (gitignore)
│   ├── sites.example.json     # plantilla (en git)
│   ├── sites.json             # tus sitios (gitignore)
│   ├── workspaces.json        # tus proyectos (gitignore)
│   └── history.json           # historial IA (gitignore)
├── core/                      # módulos del asistente
├── voices/                    # modelo Piper (no en git)
└── cache/tts/                 # caché de audio generado
```

---

## FAQ

**¿Necesito internet?** Solo para instalar y para lo que le pedís (buscar en Google, abrir sitios). Voz e IA son 100% offline.

**¿Por qué tarda la primera vez?** Whisper carga el modelo en RAM. Las siguientes veces es inmediato.

**No reconoce bien lo que digo:** probá `"stt_whisper_model": "small"` en `config.local.json`, o aumentá `"stt_silence_secs": 2.0` si corta antes de que termines.

**¿Por qué no están mis modos/sitios en el repo?** Contienen datos personales. Están en `.gitignore`. Ver sección [Archivos personales](#archivos-personales).

**¿Cómo corro en segundo plano?** Linux: `nohup python main.py &> kanye.log &` · Windows: `pythonw main.py`

---

MIT — hacé lo que quieras con el código.
