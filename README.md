# K.A.N.Y.E.
**K**nowledge **A**ssistant **N**avigating **Y**our **E**nvironment

Asistente de voz personal, 100% local, en español. Se activa con una tecla (`Ctrl+F9`), escucha tu comando y lo ejecuta: abre apps, busca en Google, controla música, activa modos de trabajo, conversa con IA y más.

No depende de internet para reconocer tu voz ni para hablar. Todo corre en tu máquina.

---

## Índice

1. [Requisitos](#1-requisitos)
2. [Instalación rápida](#2-instalación-rápida)
3. [Instalación manual paso a paso](#3-instalación-manual-paso-a-paso)
   - 3.1 [Python](#31-python)
   - 3.2 [Clonar el repositorio](#32-clonar-el-repositorio)
   - 3.3 [Dependencias Python](#33-dependencias-python)
   - 3.4 [Dependencias del sistema (Linux)](#34-dependencias-del-sistema-linux)
   - 3.5 [Ollama y modelos de IA](#35-ollama-y-modelos-de-ia)
   - 3.6 [Modelo de voz (TTS)](#36-modelo-de-voz-tts)
   - 3.7 [Modelo de reconocimiento de voz (STT)](#37-modelo-de-reconocimiento-de-voz-stt)
4. [Configuración](#4-configuración)
   - 4.1 [config.json](#41-configjson)
   - 4.2 [Ajustar para laptops con poca RAM](#42-ajustar-para-laptops-con-poca-ram)
5. [Primeros pasos](#5-primeros-pasos)
6. [Comandos disponibles](#6-comandos-disponibles)
   - 6.1 [Abrir aplicaciones](#61-abrir-aplicaciones)
   - 6.2 [Cerrar aplicaciones](#62-cerrar-aplicaciones)
   - 6.3 [Buscar en internet](#63-buscar-en-internet)
   - 6.4 [Abrir carpetas](#64-abrir-carpetas)
   - 6.5 [Abrir sitios web guardados](#65-abrir-sitios-web-guardados)
   - 6.6 [Música](#66-música)
   - 6.7 [Control multimedia](#67-control-multimedia)
   - 6.8 [Modos de trabajo](#68-modos-de-trabajo)
   - 6.9 [Archivos](#69-archivos)
   - 6.10 [Conversación con IA](#610-conversación-con-ia)
   - 6.11 [Salir](#611-salir)
7. [Modos de trabajo](#7-modos-de-trabajo)
8. [Sitios web guardados](#8-sitios-web-guardados)
9. [Workspaces (proyectos)](#9-workspaces-proyectos)
10. [Hotkey en Linux — Solución de problemas](#10-hotkey-en-linux--solución-de-problemas)
11. [Estructura del proyecto](#11-estructura-del-proyecto)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)

---

## 1. Requisitos

| Requisito | Mínimo | Recomendado |
|---|---|---|
| Python | 3.10+ | 3.11+ |
| RAM | 4 GB | 8 GB o más |
| Espacio en disco | ~3 GB | ~5 GB |
| Micrófono | Cualquiera | — |
| Parlantes / auriculares | Cualquiera | — |
| Conexión a internet | Solo para la instalación | — |

**Sistemas operativos soportados:**
- Linux (Ubuntu, Debian, Fedora, Arch, Manjaro, openSUSE y derivados)
- Windows 10 / 11

---

## 2. Instalación rápida

Si querés instalar todo automáticamente en un solo paso:

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/K.A.N.Y.E.git
cd K.A.N.Y.E

# 2. Ejecutar el instalador
python install.py

# 3. Iniciar el asistente
python main.py
```

El instalador se encarga de:
- Instalar todas las dependencias Python
- Instalar dependencias del sistema en Linux (portaudio, playerctl, etc.)
- Descargar e instalar Ollama si no está
- Bajar los modelos de IA (`phi4-mini` y `qwen2.5:1.5b`)
- Descargar el modelo de voz en español
- Descargar el modelo de reconocimiento de voz Whisper

> Si preferís control total sobre cada paso, seguí la instalación manual abajo.

---

## 3. Instalación manual paso a paso

### 3.1 Python

K.A.N.Y.E. requiere Python 3.10 o superior.

**Linux:**
```bash
# Ubuntu / Debian
sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Arch / Manjaro
sudo pacman -S python python-pip
```

**Windows:**
1. Descargá Python desde [python.org/downloads](https://www.python.org/downloads/)
2. Durante la instalación, marcá la casilla **"Add Python to PATH"**
3. Verificá que funcione:
   ```cmd
   python --version
   ```

---

### 3.2 Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/K.A.N.Y.E.git
cd K.A.N.Y.E
```

**Opcional — crear un entorno virtual (recomendado):**
```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

---

### 3.3 Dependencias Python

```bash
pip install -r requirements.txt
```

Esto instala:

| Paquete | Para qué sirve |
|---|---|
| `faster-whisper` | Reconocimiento de voz offline (STT) |
| `piper-tts` | Síntesis de voz offline (TTS) |
| `ollama` | Conexión con modelos de IA locales |
| `pynput` | Hotkey global (Ctrl+F9) |
| `sounddevice` | Captura y reproducción de audio |
| `soundfile` | Lectura de archivos WAV |
| `numpy` | Procesamiento de audio |
| `rapidfuzz` | Búsqueda difusa de apps y procesos |
| `psutil` | Gestión de procesos del sistema |
| `pyautogui` | Control multimedia en Windows |
| `yt-dlp` | Búsqueda de música en YouTube |

---

### 3.4 Dependencias del sistema (Linux)

Las librerías de audio y control multimedia no se instalan con pip. Instalálas según tu distro:

**Ubuntu / Debian / Linux Mint / Pop!_OS:**
```bash
sudo apt update
sudo apt install portaudio19-dev libsndfile1 playerctl pulseaudio-utils
```

**Fedora:**
```bash
sudo dnf install portaudio-devel libsndfile-devel playerctl pulseaudio-utils
```

**Arch / Manjaro / EndeavourOS:**
```bash
sudo pacman -S portaudio libsndfile playerctl libpulse
```

**openSUSE:**
```bash
sudo zypper install portaudio-devel libsndfile-devel playerctl
```

> `playerctl` controla la reproducción multimedia (play, pausa, siguiente).
> `pulseaudio-utils` (`pactl`) controla el volumen del sistema.
> `portaudio` es necesario para capturar audio del micrófono.

---

### 3.5 Ollama y modelos de IA

Ollama es el motor que corre los modelos de IA localmente.

**Instalar Ollama:**

*Linux (automático):*
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

*Windows:*
1. Descargá el instalador desde [ollama.com/download](https://ollama.com/download)
2. Ejecutalo y seguí los pasos
3. Ollama quedará corriendo como servicio en segundo plano

**Verificar que Ollama esté corriendo:**
```bash
ollama list
```

**Descargar los modelos necesarios:**

```bash
# Modelo de conversación (~2.5 GB descarga, ~2.5 GB RAM)
ollama pull phi4-mini

# Modelo clasificador de intención (~1 GB descarga, ~1 GB RAM)
ollama pull qwen2.5:1.5b
```

> La primera descarga puede tardar varios minutos según tu conexión.

**Verificar que los modelos estén disponibles:**
```bash
ollama list
# Deberías ver phi4-mini y qwen2.5:1.5b en la lista
```

---

### 3.6 Modelo de voz (TTS)

K.A.N.Y.E. usa Piper para generar voz en español. Necesitás descargar el modelo de voz.

**Crear la carpeta si no existe:**
```bash
mkdir -p voices
```

**Descargar el modelo (dos archivos):**

*Linux / macOS:*
```bash
# Archivo del modelo (~63 MB)
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx" \
     -o voices/es_ES-davefx-medium.onnx

# Archivo de configuración
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json" \
     -o voices/es_ES-davefx-medium.onnx.json
```

*Windows (PowerShell):*
```powershell
# Crear carpeta
New-Item -ItemType Directory -Force -Path voices

# Descargar modelo
Invoke-WebRequest `
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx" `
  -OutFile "voices\es_ES-davefx-medium.onnx"

# Descargar configuración
Invoke-WebRequest `
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json" `
  -OutFile "voices\es_ES-davefx-medium.onnx.json"
```

**Verificar:**
```bash
ls voices/
# Debe mostrar: es_ES-davefx-medium.onnx  es_ES-davefx-medium.onnx.json
```

---

### 3.7 Modelo de reconocimiento de voz (STT)

El modelo Whisper se descarga automáticamente la primera vez que iniciás K.A.N.Y.E. También podés precargarlo ahora:

```bash
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8'); print('Whisper listo.')"
```

Esto descarga el modelo `base` (~74 MB) y lo guarda en caché. No necesitás repetirlo.

---

## 4. Configuración

### 4.1 config.json

Toda la configuración del asistente está en `config/config.json`:

```json
{
  "hotkey": "ctrl+f9",
  "stt_backend": "whisper",
  "stt_whisper_model": "base",
  "stt_silence_threshold": 500,
  "stt_silence_secs": 1.5,
  "stt_max_secs": 10.0,
  "chat_model": "phi4-mini",
  "intent_model": "qwen2.5:1.5b",
  "use_llm_classifier": true,
  "voice_model": "voices/es_ES-davefx-medium.onnx",
  "tts_cache_dir": "cache/tts",
  "language": "es"
}
```

| Clave | Valor por defecto | Descripción |
|---|---|---|
| `hotkey` | `"ctrl+f9"` | Combinación de teclas para activar el asistente |
| `stt_whisper_model` | `"base"` | Tamaño del modelo Whisper (`tiny`, `base`, `small`) |
| `stt_silence_threshold` | `500` | Umbral de volumen para detectar silencio (0–32768) |
| `stt_silence_secs` | `1.5` | Segundos de silencio para cortar la grabación |
| `stt_max_secs` | `10.0` | Duración máxima de grabación por comando |
| `chat_model` | `"phi4-mini"` | Modelo Ollama para conversación |
| `intent_model` | `"qwen2.5:1.5b"` | Modelo Ollama para clasificar intenciones ambiguas |
| `use_llm_classifier` | `true` | Usar el clasificador LLM para frases ambiguas |
| `language` | `"es"` | Idioma para Whisper |

**Cambiar el hotkey:**
```json
"hotkey": "ctrl+space"
```
Combinaciones soportadas: `ctrl`, `shift`, `alt`, `f1`–`f12`, letras, `space`.

---

### 4.2 Ajustar para laptops con poca RAM

**4 GB RAM o menos** — usa solo un modelo pequeño:
```json
{
  "chat_model": "qwen2.5:1.5b",
  "intent_model": "qwen2.5:1.5b",
  "use_llm_classifier": false,
  "stt_whisper_model": "tiny"
}
```
```bash
# Solo necesitás descargar este modelo
ollama pull qwen2.5:1.5b
```

**6–8 GB RAM** — balance calidad/rendimiento:
```json
{
  "chat_model": "phi4-mini",
  "intent_model": "qwen2.5:1.5b",
  "use_llm_classifier": false,
  "stt_whisper_model": "base"
}
```

**16 GB RAM o más** — configuración completa (por defecto):
```json
{
  "chat_model": "phi4-mini",
  "intent_model": "qwen2.5:1.5b",
  "use_llm_classifier": true,
  "stt_whisper_model": "base"
}
```

**Comparativa de modelos Whisper:**

| Modelo | Tamaño | Velocidad | Precisión |
|---|---|---|---|
| `tiny` | ~39 MB | Muy rápido | Básica |
| `base` | ~74 MB | Rápido | Buena ✓ |
| `small` | ~244 MB | Moderado | Muy buena |

---

## 5. Primeros pasos

**Iniciar el asistente:**
```bash
python main.py
```

Verás algo como:
```
K.A.N.Y.E. iniciado.
Presioná [CTRL+F9] para activar el asistente.
Decí 'salir' para cerrar.

Estado: esperando [CTRL+F9]...
```

**Flujo básico de uso:**

1. **Presioná `Ctrl+F9`** — K.A.N.Y.E. dice "Te escucho"
2. **Decí tu comando** en voz alta — por ejemplo: *"abre YouTube"*
3. K.A.N.Y.E. procesa y ejecuta la acción
4. Vuelve a esperar la tecla

> La primera vez que hablás, Whisper carga el modelo en RAM (~2 segundos extra). Las siguientes veces es inmediato.

---

## 6. Comandos disponibles

Todos los comandos se dicen después de presionar `Ctrl+F9`.

---

### 6.1 Abrir aplicaciones

```
abre [nombre de la app]
abrir [nombre de la app]
lanza [nombre de la app]
ejecuta [nombre de la app]
```

**Ejemplos:**
```
abre Visual Studio Code
abrir Steam
lanza Discord
abre el navegador
abrir calculadora
```

> K.A.N.Y.E. hace búsqueda difusa — no tenés que decir el nombre exacto. *"visual studio"*, *"vscode"* o *"código"* pueden funcionar.

**En Linux:** busca en `/usr/share/applications/` y `~/.local/share/applications/` (incluyendo apps de Flatpak).

**En Windows:** busca en el Menú Inicio (`%APPDATA%` y `%PROGRAMDATA%`).

---

### 6.2 Cerrar aplicaciones

```
cierra [nombre de la app]
cerrar [nombre de la app]
termina [nombre de la app]
mata [nombre de la app]
```

**Ejemplos:**
```
cierra Chrome
termina Spotify
mata el navegador
```

> Usa búsqueda difusa sobre los procesos activos. Cierra todos los procesos con ese nombre.

---

### 6.3 Buscar en internet

```
busca [lo que querés buscar]
buscar [lo que querés buscar]
googlea [lo que querés buscar]
investiga [lo que querés buscar]
```

**Ejemplos:**
```
busca cómo instalar Docker en Linux
googlea árboles B en estructuras de datos
investiga recetas con pollo
```

> Abre una nueva pestaña en tu navegador predeterminado con la búsqueda en Google.

---

### 6.4 Abrir carpetas

```
abre [nombre de la carpeta]
```

Carpetas reconocidas:

| Lo que decís | Carpeta que abre |
|---|---|
| `descargas` / `downloads` | ~/Downloads |
| `documentos` / `documents` | ~/Documents |
| `escritorio` / `desktop` | ~/Desktop |
| `imágenes` / `pictures` | ~/Pictures |
| `videos` | ~/Videos |
| `música` / `music` | ~/Music |

**Ejemplos:**
```
abre descargas
abre documentos
abrir escritorio
```

---

### 6.5 Abrir sitios web guardados

```
abre sitio [nombre del sitio]
abre página [nombre del sitio]
```

**Ejemplos:**
```
abre sitio YouTube
abre página GitHub
abre sitio WhatsApp
abre página Google Classroom
```

Sitios preconfigurados: YouTube, YouTube Music, GitHub, ChatGPT, Gmail, Google Drive, Google Docs, Notion, Figma, Pinterest, WhatsApp Web, Classroom, Unitec, Canvas.

> Para agregar más sitios, editá `config/sites.json` (ver sección [8](#8-sitios-web-guardados)).

---

### 6.6 Música

```
pon [canción o artista]
reproduce [canción o artista]
toca [canción o artista]
busca canción [canción o artista]
```

**Ejemplos:**
```
pon Runaway de Kanye West
reproduce After Hours The Weeknd
toca música lo-fi
pon algo de Bad Bunny
```

> Busca el primer resultado en YouTube y lo abre en YouTube Music directamente.

---

### 6.7 Control multimedia

Estos comandos funcionan sobre cualquier reproductor activo.

| Comando | Acción |
|---|---|
| `pausa` / `reanuda` / `continua` | Play / Pausa |
| `siguiente` / `siguiente canción` | Siguiente pista |
| `anterior` / `canción anterior` | Pista anterior |
| `sube volumen` / `más volumen` | Subir volumen |
| `baja volumen` / `menos volumen` | Bajar volumen |
| `silencia` / `silencio` / `mute` | Silenciar |

**En Linux:** usa `playerctl` y `pactl` — funciona con Spotify, VLC, Rhythmbox, navegadores, etc.
**En Windows:** usa teclas multimedia del sistema.

---

### 6.8 Modos de trabajo

Los modos abren un conjunto de apps, URLs y carpetas de una vez.

```
activa modo [nombre]
modo [nombre]
```

**Ejemplos:**
```
activa modo gaming
modo trabajo
activa modo estudio
```

**Gestionar modos:**

| Comando | Acción |
|---|---|
| `crea modo [nombre]` | Crear un nuevo modo (interactivo) |
| `edita modo [nombre]` | Editar un modo existente |
| `elimina modo [nombre]` | Eliminar un modo |
| `modos` / `lista modos` | Ver todos los modos guardados |

> Ver sección [7](#7-modos-de-trabajo) para detalle completo de cómo crear modos.

---

### 6.9 Archivos

Los comandos de archivo operan dentro de un **workspace** (proyecto configurado).

**Leer un archivo:**
```
lee archivo [nombre del archivo]
lee archivo main.py
lee archivo src/utils.js en proyecto web
```

**Buscar texto en un archivo:**
```
busca en archivo [archivo] el texto [texto]
busca en archivo main.py el texto LAST_INTERACTION
```

**Hacer backup:**
```
haz backup de archivo [nombre del archivo]
haz backup de archivo main.py
```

**Reemplazar texto en un archivo:**
```
reemplaza [texto viejo] por [texto nuevo] en archivo [nombre del archivo]
reemplaza print por console.log en archivo index.js
```

> Los comandos de archivo piden confirmación antes de modificar. Siempre se hace backup automático antes de reemplazar.

---

### 6.10 Conversación con IA

Cualquier cosa que no sea un comando del sistema se envía al modelo de conversación:

```
qué es un árbol B
cómo optimizo este algoritmo
qué opinas del diseño minimalista
dame ideas para mi proyecto
explícame qué es recursividad
```

La IA tiene personalidad de **K.A.N.Y.E.**: directa, visionaria, sin rodeos. Mantiene contexto de la conversación (últimas 6 interacciones).

> Si venías conversando y decís algo ambiguo, K.A.N.Y.E. asume que seguís en conversación. Para dar un comando claro, usá palabras clave como "abre", "busca", "cierra", etc.

---

### 6.11 Salir

```
salir
cerrar
exit
quit
```

---

## 7. Modos de trabajo

Los modos son configuraciones que abren todo lo que necesitás para una actividad de un solo golpe.

### Crear un modo

Presioná `Ctrl+F9` y decí:
```
crea modo gaming
```

K.A.N.Y.E. te preguntará interactivamente (en la terminal):

```
K.A.N.Y.E.: Creando modo 'gaming'.

Apps a abrir, separadas por coma. Ej: steam, discord, chrome
Apps: steam, discord

URLs a abrir, separadas por coma. Si no hay, escribe no.
URLs: no

Carpetas a abrir, separadas por coma. Si no hay, escribe no.
Carpetas: no

¿Cerrar apps antes de activar este modo? sí/no: sí

Mensaje final del modo. Si lo dejas vacío, usaré uno automático.
Mensaje: Modo gaming activado. A dominar.

K.A.N.Y.E.: Resumen del modo:
{
    "close_before": true,
    "apps": ["steam", "discord"],
    "urls": [],
    "folders": [],
    "message": "Modo gaming activado. A dominar."
}

¿Guardar este modo? sí/no: sí
```

### Activar un modo

```
activa modo gaming
```

K.A.N.Y.E. cierra las apps que tenga configuradas, luego abre Steam, Discord, y dice el mensaje.

### Editar un modo

```
edita modo gaming
```

Podés editar apps, URLs, carpetas, mensaje o todo junto.

### Los modos se guardan en `config/modes.json`

Podés editarlos directamente si querés:

```json
{
    "gaming": {
        "close_before": true,
        "apps": ["steam", "discord"],
        "urls": [],
        "folders": [],
        "message": "Modo gaming activado."
    },
    "trabajo": {
        "close_before": false,
        "apps": ["visual studio code"],
        "urls": ["https://github.com", "https://notion.so"],
        "folders": ["documentos"],
        "message": "Modo trabajo. A construir."
    }
}
```

---

## 8. Sitios web guardados

Los sitios están en `config/sites.json`. Podés agregar los que quieras:

```json
{
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "mi proyecto": "https://tuproyecto.vercel.app",
    "figma": "https://www.figma.com",
    "whatsapp": "https://web.whatsapp.com"
}
```

La búsqueda es difusa — si decís *"abre sitio you tube"* o *"abre página utube"*, va a encontrar YouTube igual.

---

## 9. Workspaces (proyectos)

Los workspaces definen en qué carpetas puede operar K.A.N.Y.E. para los comandos de archivo. Están en `config/workspaces.json`:

```json
{
    "kanye": "/ruta/a/tu/proyecto/kanye",
    "web": "/home/aaron/proyectos/mi-web",
    "universidad": "/home/aaron/documentos/unitec"
}
```

**Cómo especificar el workspace en un comando de archivo:**
```
lee archivo index.html en proyecto web
haz backup de archivo App.js en el proyecto web
busca en archivo main.py el texto import del proyecto kanye
```

Si no especificás proyecto, usa `kanye` por defecto.

**Actualizar la ruta de tu workspace:**
1. Abrí `config/workspaces.json`
2. Cambiá la ruta a tu carpeta actual:
   ```json
   { "kanye": "/home/tu_usuario/K.A.N.Y.E" }
   ```

---

## 10. Hotkey en Linux — Solución de problemas

### El hotkey no responde

**Causa más común:** tu usuario no tiene permiso para leer dispositivos de entrada.

**Solución:**
```bash
sudo usermod -aG input $USER
# Cerrar sesión y volver a entrar
```

**Alternativa — correr K.A.N.Y.E. con sudo (temporal):**
```bash
sudo python main.py
```

### En Wayland (GNOME, KDE Plasma, Sway)

`pynput` tiene soporte limitado en Wayland. Opciones:

**Opción 1 — Cambiar a sesión X11:**
En la pantalla de inicio de sesión, elegí *"GNOME en X11"* o *"Plasma (X11)"*.

**Opción 2 — Modo terminal (fallback automático):**
Si el hotkey falla, K.A.N.Y.E. activa automáticamente el modo terminal:
```
K.A.N.Y.E.: Modo terminal activo. Presioná Enter para activar.
```
Simplemente presioná **Enter** en la terminal donde corre K.A.N.Y.E.

### El hotkey interfiere con otra app

Cambiá la combinación en `config/config.json`:
```json
"hotkey": "ctrl+shift+k"
```

Opciones recomendadas que raramente interfieren:
- `ctrl+shift+k`
- `ctrl+shift+space`
- `f12`

---

## 11. Estructura del proyecto

```
K.A.N.Y.E/
├── main.py                    # Punto de entrada
├── install.py                 # Instalador automático
├── requirements.txt           # Dependencias Python
│
├── config/
│   ├── config.json            # Configuración principal
│   ├── modes.json             # Modos de trabajo guardados
│   ├── sites.json             # Sitios web guardados
│   └── workspaces.json        # Proyectos/workspaces
│
├── core/
│   ├── config_loader.py       # Carga config.json con defaults
│   ├── platform_utils.py      # Detección de OS (is_windows / is_linux)
│   ├── hotkey_listener.py     # Escucha el hotkey (pynput)
│   ├── speech_to_text.py      # Reconocimiento de voz (Whisper offline)
│   ├── text_to_speech.py      # Síntesis de voz (Piper, con caché)
│   ├── text_normalizer.py     # Correcciones de errores de STT
│   ├── intent_router.py       # Clasifica comandos por reglas
│   ├── llm_intent.py          # Clasifica intenciones ambiguas con LLM
│   ├── local_llm.py           # Conversación con IA (phi4-mini)
│   ├── app_resolver.py        # Búsqueda de apps (Win: .lnk / Linux: .desktop)
│   ├── system_actions.py      # Abrir aplicaciones
│   ├── process_actions.py     # Cerrar procesos
│   ├── folder_actions.py      # Abrir carpetas del sistema
│   ├── site_actions.py        # Abrir sitios web guardados
│   ├── web_search.py          # Búsqueda en Google
│   ├── music_actions.py       # Música en YouTube Music
│   ├── media_actions.py       # Control multimedia (Win/Linux)
│   ├── mode_actions.py        # Gestión de modos de trabajo
│   ├── file_actions.py        # Operaciones de archivo (con workspaces)
│   └── responses.py           # Frases de respuesta aleatorias
│
├── voices/
│   ├── es_ES-davefx-medium.onnx       # Modelo de voz
│   └── es_ES-davefx-medium.onnx.json  # Configuración del modelo
│
└── cache/
    └── tts/                   # Caché de frases sintetizadas (WAV)
```

---

## 12. Preguntas frecuentes

**¿Necesito internet para usar K.A.N.Y.E.?**
No. El reconocimiento de voz (Whisper), la síntesis de voz (Piper) y la IA (Ollama) corren 100% local. Solo necesitás internet para la instalación inicial y para abrir sitios o buscar en Google cuando le pedís que lo haga.

---

**¿Por qué tarda la primera vez que hablo?**
Whisper carga el modelo en RAM la primera vez. Desde la segunda activación en adelante es inmediato.

---

**¿Por qué no reconoce bien lo que digo?**
1. Asegurate de hablar cerca del micrófono
2. Reducí el ruido de fondo
3. Probá el modelo `small` en `config.json` para mejor precisión (requiere más tiempo de procesado):
   ```json
   "stt_whisper_model": "small"
   ```
4. Ajustá el umbral de silencio si K.A.N.Y.E. corta antes de que termines:
   ```json
   "stt_silence_secs": 2.0
   ```

---

**¿Puedo usar otro idioma?**
El asistente está diseñado para español. Para cambiar el idioma de reconocimiento:
```json
"language": "en"
```
Pero tendrías que adaptar también los comandos en `intent_router.py` y los prompts en `local_llm.py` y `llm_intent.py`.

---

**¿Cómo agrego una app que K.A.N.Y.E. no encuentra?**

*En Linux:* verificá que la app tenga un archivo `.desktop` en `/usr/share/applications/` o `~/.local/share/applications/`.

*En Windows:* verificá que la app aparezca en el Menú Inicio.

Si no, podés agregar apps personalizadas editando `config/modes.json` con la ruta directa como URL o usando el sistema de modos.

---

**¿Cómo cambio la voz?**
Descargá otro modelo de Piper desde [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices), colocalo en `voices/` y actualizá `config/config.json`:
```json
"voice_model": "voices/es_ES-OTRO_MODELO.onnx"
```

---

**¿Cómo desactivo el clasificador LLM para ahorrar RAM?**
```json
"use_llm_classifier": false
```
Con esto, si el asistente no reconoce el comando por reglas, va directo a conversación. Usá frases más directas para los comandos.

---

**¿Puedo correr K.A.N.Y.E. en segundo plano?**

*Linux:*
```bash
nohup python main.py &> kanye.log &
```

*Windows:*
```cmd
pythonw main.py
```
O creá un acceso directo con `pythonw.exe` como ejecutable.

---

**¿Dónde se guarda el caché de voz?**
En `cache/tts/`. Cada frase que K.A.N.Y.E. dice con frecuencia se guarda como `.wav` para no regenerarla cada vez. Podés borrar la carpeta si querés limpiar el caché — se regenerará automáticamente.

---

## Licencia

MIT — hacé lo que quieras con el código.
