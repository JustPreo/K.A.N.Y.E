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
  "intent_model": "qwen2.5:1.5b",
  "stt_whisper_model": "base",
  "use_llm_classifier": true,
  "language": "es"
}
```

**Por RAM disponible:**

| RAM | `chat_model` | `stt_whisper_model` | `use_llm_classifier` |
|---|---|---|---|
| ≤ 4 GB | `qwen2.5:1.5b` | `tiny` | `false` |
| 6–8 GB | `phi4-mini` | `base` | `false` |
| 16 GB+ | `phi4-mini` | `base` | `true` |

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

## Comandos

Todos se dicen después de presionar `Ctrl+F9`.

### Apps y sistema

| Di... | Acción |
|---|---|
| `abre / lanza / ejecuta [app]` | Abrir aplicación (búsqueda difusa) |
| `cierra / termina / mata [app]` | Cerrar proceso |
| `abre [descargas/documentos/escritorio/...]` | Abrir carpeta del sistema |
| `salir` | Cerrar K.A.N.Y.E. |

### Web y búsqueda

| Di... | Acción |
|---|---|
| `busca / googlea [tema]` | Buscar en Google |
| `abre sitio / abre página [nombre]` | Abrir sitio guardado |
| `guarda sitio [nombre]` | Guardar nuevo sitio (pide URL) |

### Música y multimedia

| Di... | Acción |
|---|---|
| `pon / reproduce / toca [canción]` | Abrir en YouTube Music |
| `pausa` / `reanuda` | Play/pausa |
| `siguiente` / `anterior` | Cambiar pista |
| `sube volumen` / `baja volumen` / `silencia` | Volumen |

### Teclado por voz

| Di... | Acción |
|---|---|
| `escribe [texto]` | Escribir texto (soporta tildes/ñ) |
| `escribe en mayúsculas [texto]` | Escribir en MAYÚSCULAS |
| `selecciona todo` | Ctrl+A |
| `copia` / `pega` / `corta` | Ctrl+C / V / X |
| `deshace` / `rehace` | Ctrl+Z / Y |
| `guarda el archivo` | Ctrl+S |
| `presiona enter/tab/escape` | Tecla individual |
| `cierra ventana` / `cambia ventana` | Alt+F4 / Alt+Tab |
| `nueva pestaña` / `cierra pestaña` / `recarga` | Ctrl+T / W / F5 |

### Modos de trabajo

| Di... | Acción |
|---|---|
| `activa modo [nombre]` | Abrir apps/URLs/carpetas configuradas |
| `crea modo [nombre]` | Crear modo (interactivo en terminal) |
| `edita modo [nombre]` | Editar modo existente |
| `elimina modo [nombre]` | Eliminar modo |
| `modos` | Listar modos disponibles |
| `desbloquea` | Desactivar focus mode |
| `estado focus` | Ver tiempo restante del focus |

### Archivos

| Di... | Acción |
|---|---|
| `lee archivo [archivo]` | Mostrar contenido |
| `busca en archivo [archivo] el texto [texto]` | Buscar texto |
| `haz backup de archivo [archivo]` | Crear backup |
| `reemplaza [viejo] por [nuevo] en archivo [archivo]` | Reemplazar texto |

Podés especificar workspace: `lee archivo main.py en proyecto web`

### IA y historial

| Di... | Acción |
|---|---|
| Cualquier pregunta | Conversación con phi4-mini |
| `borra historial` | Limpiar contexto de conversación |

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
