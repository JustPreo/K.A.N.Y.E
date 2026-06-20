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
   - 4.1 [config.json — valores por defecto](#41-configjson--valores-por-defecto)
   - 4.2 [config.local.json — tu configuración personal](#42-configlocaljson--tu-configuración-personal)
   - 4.3 [Ajustar para laptops con poca RAM](#43-ajustar-para-laptops-con-poca-ram)
5. [Archivos personales (gitignore)](#5-archivos-personales-gitignore)
6. [Primeros pasos](#6-primeros-pasos)
7. [Comandos disponibles](#7-comandos-disponibles)
   - 7.1 [Abrir aplicaciones](#71-abrir-aplicaciones)
   - 7.2 [Cerrar aplicaciones](#72-cerrar-aplicaciones)
   - 7.3 [Buscar en internet](#73-buscar-en-internet)
   - 7.4 [Abrir carpetas](#74-abrir-carpetas)
   - 7.5 [Abrir sitios web guardados](#75-abrir-sitios-web-guardados)
   - 7.6 [Música](#76-música)
   - 7.7 [Control multimedia](#77-control-multimedia)
   - 7.8 [Modos de trabajo](#78-modos-de-trabajo)
   - 7.9 [Teclado por voz](#79-teclado-por-voz)
   - 7.10 [Modo focus](#710-modo-focus)
   - 7.11 [Archivos](#711-archivos)
   - 7.12 [Conversación con IA](#712-conversación-con-ia)
   - 7.13 [Salir](#713-salir)
8. [Modos de trabajo](#8-modos-de-trabajo)
9. [Sitios web guardados](#9-sitios-web-guardados)
10. [Workspaces (proyectos)](#10-workspaces-proyectos)
11. [Presencia ambiental y monitor de sistema](#11-presencia-ambiental-y-monitor-de-sistema)
12. [Hotkey en Linux — Solución de problemas](#12-hotkey-en-linux--solución-de-problemas)
13. [Estructura del proyecto](#13-estructura-del-proyecto)
14. [Preguntas frecuentes](#14-preguntas-frecuentes)

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

**Crear tus archivos de configuración personal a partir de los ejemplos:**

```bash
cp config/modes.example.json config/modes.json
cp config/sites.example.json config/sites.json
```

Editá esos archivos con tus modos y sitios. No se subirán al repo (ver [sección 5](#5-archivos-personales-gitignore)).

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

### 4.1 config.json — valores por defecto

`config/config.json` está en el repositorio y contiene los valores por defecto para cualquiera que clone el proyecto:

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

---

### 4.2 config.local.json — tu configuración personal

Para sobreescribir valores de `config.json` **sin tocar el archivo del repo**, creá `config/config.local.json`. Este archivo está en `.gitignore` — solo existe en tu máquina.

```bash
# Crear config personal (solo la primera vez)
touch config/config.local.json
```

Ejemplo — cambiar hotkey y modelo:
```json
{
  "hotkey": "ctrl+shift+k",
  "chat_model": "llama3.2",
  "stt_whisper_model": "small"
}
```

Solo necesitás incluir las claves que querés cambiar. El resto se toma de `config.json`.

> Si ambos archivos existen, `config.local.json` tiene prioridad sobre `config.json`.

---

### 4.3 Ajustar para laptops con poca RAM

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

## 5. Archivos personales (gitignore)

Los archivos que contienen tu configuración personal **no se suben al repositorio**. Existen solo en tu disco.

| Archivo | En git | Descripción |
|---|---|---|
| `config/config.json` | ✓ | Valores por defecto (para todos) |
| `config/config.local.json` | ✗ | Tu hotkey, tus modelos, etc. |
| `config/modes.json` | ✗ | Tus modos de trabajo personales |
| `config/sites.json` | ✗ | Tus sitios guardados |
| `config/workspaces.json` | ✗ | Tus rutas de proyectos locales |
| `config/history.json` | ✗ | Historial de conversación con la IA |

Para que quien clone el repo sepa el formato, hay versiones de ejemplo:
- `config/modes.example.json` — plantilla de modos
- `config/sites.example.json` — plantilla de sitios

**Primera vez que clonás:**
```bash
cp config/modes.example.json config/modes.json
cp config/sites.example.json config/sites.json
# Luego editá esos archivos con tus datos
```

Los archivos `workspaces.json` e `history.json` se crean automáticamente al usar el asistente.

---

## 6. Primeros pasos

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

## 7. Comandos disponibles

Todos los comandos se dicen después de presionar `Ctrl+F9`.

---

### 7.1 Abrir aplicaciones

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

### 7.2 Cerrar aplicaciones

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

### 7.3 Buscar en internet

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

### 7.4 Abrir carpetas

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

### 7.5 Abrir sitios web guardados

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

Los sitios disponibles dependen de lo que tengas en tu `config/sites.json`. El repo incluye `config/sites.example.json` como referencia.

> Para agregar sitios por voz: *"guarda sitio nombre"* y K.A.N.Y.E. te pedirá la URL.

---

### 7.6 Música

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

### 7.7 Control multimedia

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

### 7.8 Modos de trabajo

Los modos abren un conjunto de apps, URLs y carpetas de una vez. Opcionalmente pueden activar el **modo focus** (bloqueo de sitios).

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

> Ver sección [8](#8-modos-de-trabajo) para detalle completo, incluyendo cómo configurar el focus.

---

### 7.9 Teclado por voz

Escribí texto o ejecutá atajos de teclado sin tocar el teclado.

**Escribir texto:**
```
escribe Hola mundo
escribí este es mi texto
dictar una idea que tuve
teclea contraseña segura123
escribe en mayúsculas TÍTULO IMPORTANTE
```

El texto se pega vía portapapeles — soporta tildes, ñ y cualquier carácter unicode.

**Atajos de teclado:**

| Comando | Teclas |
|---|---|
| `presiona enter` | Enter |
| `presiona tab` | Tab |
| `presiona escape` | Escape |
| `selecciona todo` | Ctrl+A |
| `copia` / `copiar` | Ctrl+C |
| `pega` / `pegar` | Ctrl+V |
| `corta` / `cortar` | Ctrl+X |
| `deshace` / `deshacer` | Ctrl+Z |
| `rehace` / `rehacer` | Ctrl+Y |
| `guarda el archivo` | Ctrl+S |
| `cierra ventana` | Alt+F4 |
| `cambia ventana` | Alt+Tab |
| `nueva pestaña` | Ctrl+T |
| `cierra pestaña` | Ctrl+W |
| `recarga` / `recargar` | F5 |
| `va atrás` | Alt+← |

---

### 7.10 Modo focus

Bloquea sitios distractores editando `/etc/hosts` por un tiempo definido.

```
activa modo estudio          # activa focus si el modo lo tiene configurado
desbloquea                   # desactiva el focus antes de tiempo
estado focus                 # cuánto tiempo queda y qué sitios están bloqueados
```

> En Linux requiere `sudo`. Ver sección [8](#8-modos-de-trabajo) para configurar `sudoers` sin contraseña.

---

### 7.11 Archivos

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

### 7.12 Conversación con IA

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

### 7.13 Salir

```
salir
cerrar
exit
quit
```

---

## 8. Modos de trabajo

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

Este archivo es **personal** — no está en el repositorio. Copialo desde el ejemplo al clonar:
```bash
cp config/modes.example.json config/modes.json
```

Podés editarlo directamente o usar los comandos de voz. Formato completo:

```json
{
    "trabajo": {
        "close_before": false,
        "apps": ["visual studio code"],
        "urls": ["https://github.com"],
        "folders": ["documentos"],
        "message": "Modo trabajo. A construir."
    },
    "estudio": {
        "close_before": false,
        "apps": [],
        "urls": [],
        "folders": [],
        "message": "Modo estudio activado. Sin distracciones.",
        "focus": {
            "enabled": true,
            "duration_minutes": 50,
            "blocked_sites": [
                "youtube.com", "twitter.com", "x.com",
                "instagram.com", "reddit.com", "tiktok.com"
            ]
        }
    }
}
```

### Focus en un modo

Agregá una clave `"focus"` al modo para bloquear sitios automáticamente al activarlo:

| Clave | Descripción |
|---|---|
| `enabled` | `true` para activar el bloqueo |
| `duration_minutes` | Minutos de bloqueo (el timer desbloquea automáticamente) |
| `blocked_sites` | Lista de dominios a bloquear (sin `www.` ni `https://`) |

**Requisito en Linux — sudo sin contraseña para `/etc/hosts`:**

```bash
sudo visudo
# Agregá esta línea (reemplazá TU_USUARIO):
TU_USUARIO ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts
```

---

## 9. Sitios web guardados

Los sitios están en `config/sites.json` — archivo **personal**, no está en el repo. Copialo desde el ejemplo:

```bash
cp config/sites.example.json config/sites.json
```

Formato:
```json
{
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "mi proyecto": "https://tuproyecto.vercel.app"
}
```

**Agregar sitios por voz:**
```
guarda sitio mi proyecto
# K.A.N.Y.E. te pregunta la URL
```

La búsqueda es difusa — *"abre sitio you tube"* o *"abre página utube"* encuentran YouTube igual.

---

## 10. Workspaces (proyectos)

Los workspaces definen en qué carpetas puede operar K.A.N.Y.E. para los comandos de archivo. Están en `config/workspaces.json` — archivo **personal**, no está en el repo (se crea automáticamente la primera vez que usás comandos de archivo).

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

## 11. Presencia ambiental y monitor de sistema

K.A.N.Y.E. corre dos hilos de fondo que influyen en tu computadora mientras trabajás.

### Presencia ambiental

Envía notificaciones de escritorio con frases motivacionales estilo Kanye en hitos de tiempo:

| Hito | Notificación |
|---|---|
| 30 min | Primera frase |
| 60 min | Segunda frase |
| 90, 120, 180, 240 min | Frases adicionales |

Las frases las genera el LLM basadas en qué modo tenés activo. Si no hay LLM disponible, usa frases de respaldo.

Las notificaciones llegan vía:
1. `plyer` (cross-platform)
2. `notify-send` en Linux (fallback)
3. Impresión en terminal (último recurso)

### Monitor de sistema

Monitorea recursos cada 30 segundos y comenta con voz + notificación si:

| Métrica | Umbral | Cooldown |
|---|---|---|
| CPU | > 85% por más de 60 seg | 5 min |
| RAM | > 90% | 10 min |
| Batería | < 15% y desconectado | 15 min |

Los comentarios los genera el LLM. Ejemplos: *"Tu CPU está sudando más que yo en mi prime. Cerrá algo."*

---

## 12. Hotkey en Linux — Solución de problemas

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

## 13. Estructura del proyecto

```
K.A.N.Y.E/
├── main.py                    # Punto de entrada
├── install.py                 # Instalador automático
├── requirements.txt           # Dependencias Python
│
├── config/
│   ├── config.json            # Valores por defecto (en git)
│   ├── config.local.json      # Tu config personal (gitignore, opcional)
│   ├── modes.example.json     # Plantilla de modos (en git)
│   ├── modes.json             # Tus modos personales (gitignore)
│   ├── sites.example.json     # Plantilla de sitios (en git)
│   ├── sites.json             # Tus sitios guardados (gitignore)
│   ├── workspaces.json        # Tus rutas de proyectos (gitignore)
│   └── history.json           # Historial de conversación (gitignore)
│
├── core/
│   ├── config_loader.py       # Carga config.json + config.local.json
│   ├── platform_utils.py      # Detección de OS (is_windows / is_linux)
│   ├── hotkey_listener.py     # Escucha el hotkey global (pynput)
│   ├── mic_calibrator.py      # Calibra umbral de silencio al inicio
│   ├── startup_checks.py      # Verifica voz, Ollama y micrófono
│   ├── speech_to_text.py      # Reconocimiento de voz (Whisper offline)
│   ├── text_to_speech.py      # Síntesis de voz (Piper, con caché)
│   ├── text_normalizer.py     # Correcciones de errores de STT
│   ├── intent_router.py       # Clasifica comandos por reglas
│   ├── llm_intent.py          # Clasifica intenciones ambiguas con LLM
│   ├── local_llm.py           # Conversación con IA + historial persistente
│   ├── app_resolver.py        # Búsqueda de apps (Win: .lnk / Linux: .desktop)
│   ├── system_actions.py      # Abrir aplicaciones
│   ├── process_actions.py     # Cerrar procesos
│   ├── folder_actions.py      # Abrir carpetas del sistema
│   ├── site_actions.py        # Abrir/guardar sitios web
│   ├── web_search.py          # Búsqueda en Google
│   ├── music_actions.py       # Música en YouTube Music
│   ├── media_actions.py       # Control multimedia (Win/Linux)
│   ├── mode_actions.py        # Gestión de modos + activación de focus
│   ├── file_actions.py        # Operaciones de archivo (con workspaces)
│   ├── keyboard_actions.py    # Escritura de texto y atajos por voz
│   ├── focus_mode.py          # Bloqueo de sitios vía /etc/hosts
│   ├── ambient.py             # Presencia ambiental (notificaciones Kanye)
│   ├── system_monitor.py      # Monitor CPU/RAM/batería con comentarios IA
│   ├── tray_icon.py           # Ícono en bandeja del sistema
│   └── responses.py           # Frases de respuesta aleatorias
│
├── voices/
│   ├── es_ES-davefx-medium.onnx       # Modelo de voz (no en git)
│   └── es_ES-davefx-medium.onnx.json  # Config del modelo (no en git)
│
└── cache/
    └── tts/                   # Caché de frases sintetizadas (WAV)
```

---

## 14. Preguntas frecuentes

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

**¿Por qué no están mis modos ni sitios en el repositorio?**
Los archivos `modes.json`, `sites.json`, `workspaces.json` e `history.json` contienen datos personales (tus apps favoritas, tus sitios, tus rutas). Están en `.gitignore` para que no se suban al repo. El repo incluye `modes.example.json` y `sites.example.json` como plantillas. Al clonar, copiálos con:
```bash
cp config/modes.example.json config/modes.json
cp config/sites.example.json config/sites.json
```

---

**¿Cómo personalizo K.A.N.Y.E. sin tocar config.json?**
Creá `config/config.local.json` con solo las claves que querés cambiar. Ese archivo está en `.gitignore` y tiene prioridad sobre `config.json`.

---

**¿Por qué el focus mode pide contraseña?**
En Linux, editar `/etc/hosts` requiere permisos de root. Para evitar que pida contraseña cada vez, configurá sudoers:
```bash
sudo visudo
# Agregá (reemplazá TU_USUARIO):
TU_USUARIO ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/hosts
```
En Windows, ejecutá K.A.N.Y.E. como administrador.

---

**¿Puedo desactivar la presencia ambiental o el monitor de sistema?**
Por ahora se inician siempre. Para desactivarlos temporalmente, comentá las líneas `ambient.start()` y `monitor.start()` en `main.py`.

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
