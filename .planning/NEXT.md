# Próximos pasos — K.A.N.Y.E.

Estado al momento de escribir esto: puntos 1, 2 y 3 de este plan original
ya están resueltos. Se agregó un punto 4 nuevo (modo "ayuda remota" con
visión) que quedó a medio probar — es lo primero a retomar, posiblemente
ya en Windows.

## 1. Probar el loop agéntico con un modelo real — ✅ hecho

Probado en vivo (no mocks) con `phi4-mini` (default de `chat_model`):
comando simple (`abrí firefox`), encadenado (`abrí brave y buscá el
clima`, 2 tools en el mismo turno), mouse (`movete el mouse a la derecha
y hacé click`), y chat puro sin tools. Los 4 casos funcionaron bien —
`phi4-mini` sostiene tool-calling multi-paso sin necesidad de subir a
`qwen2.5:7b` ni cambiar a DeepSeek.

De paso se encontró y arregló un bug real: `open_app` no veía apps
instaladas vía snap (Firefox en Ubuntu/derivados) porque
`LINUX_DESKTOP_DIRS` en `core/app_resolver.py` no incluía
`/var/lib/snapd/desktop/applications` (commit `a904e1f`).

## 2. Tools candidatas — evaluadas, 2 de 3 implementadas

- **Notas persistentes** — ✅ implementado (`core/notes_actions.py`,
  commit `ace82c4`). `add_note`/`list_notes`/`delete_note`, guardadas en
  `config/notes.json` (gitignored). Resuelve que el historial se trunca a
  24 mensajes — "recordá que..." ya no se pierde. Probado en vivo.
- **Control de ventanas** — ✅ implementado (`core/window_actions.py`,
  commit `4763ba6`). `minimize_window`/`toggle_maximize_window` sobre la
  ventana activa, con dispatcher por compositor (Hyprland/Sway/GNOME/KDE
  vía IPC nativo, fallback wmctrl/xdotool en X11, Windows y macOS).
  `wmctrl`/`xdotool` sumados a `install.py`. Probado en vivo sobre
  Hyprland. No se implementó "cambiar de escritorio" (quedó fuera de
  alcance, no evaluado).
- **Screenshot / visión** — ⏸ diferido, no implementado. Es la tool con
  mayor costo/riesgo: necesita un modelo de visión aparte corriendo junto
  a whisper+piper+chat model (presión de RAM real en laptops de 16GB o
  menos), y captura de pantalla en Wayland no es trivial sin portales.
  Es también lo único que resolvería de verdad la limitación de
  `mouse_click`/`mouse_drag` (ver nota abajo) — no vale la pena antes de
  decidir si se justifica ese costo.

**Nota sobre el mouse:** se discutió que `mouse_click`/`mouse_drag` son
casi decorativos sin visión — el agente no puede apuntar a un botón
específico, solo mover/clickear a ciegas por direcciones relativas.
`mouse_scroll` sí es útil de por sí. Se decidió dejarlos como están (no
estorban, y sirven para casos gruesos tipo cerrar notificaciones en
posiciones predecibles) — se revisita si algún día se resuelve visión.

## 3. Pulir la GUI mono una vez se vea corriendo de verdad — ✅ hecho

Se probó en vivo con capturas reales (ventana principal + Configuración).
El chip de estado y el CTA blanco **no se ven planos** — alto contraste,
se dio por bueno sin tocar nada. Se encontró y arregló un bug real de
paso: `settings_gui.py` usaba emojis (⚙🎧🤖👁💾) en headers y botones, que
en la mayoría de plataformas renderizan a color vía la fuente de emoji del
sistema — rompiendo la regla de paleta mono. Reemplazados por texto en
mayúscula (commit `54893aa`). Win+C sigue sin poder probarse en esta
sesión (fix específico de Windows, sesión corrió en Linux/Hyprland).

## 4. Modo "ayuda remota" con visión — 🚧 implementado, sin probar end-to-end

Plan completo en la sesión que lo armó (buscar en el historial de chat
"Modo 'Ayuda remota' (IT worker con visión)"). Screenshot → DeepSeek
(`deepseek-v4-flash-vision-exp`) decide una acción → se confirma con el
usuario en un diálogo con la imagen y el punto marcado → se ejecuta →
repite. Todo vive en `core/it_worker.py`, activado por el tool
`start_it_help` (`core/tools.py`). Commit `f4cc5d2`.

**Verificado en esta sesión (Hyprland/Linux):**
- `core/screen_actions.capture()` vía `grim`: OK.
- La llamada a `deepseek-v4-flash-vision-exp` funciona y describe la
  pantalla correctamente (probado con un request crudo — el wrapper
  `deepseek_client.chat_vision()` usa el mismo payload, no debería
  diferir, pero no se confirmó el wrapper en sí con un timeout más largo).

**Sin verificar — esto es lo primero a retomar:**
- El loop completo `core/it_worker.run(problem)` de punta a punta: que el
  diálogo de confirmación (`core/gui.confirm_action`, nuevo en
  `core/gui.py`) realmente aparezca con la imagen + el círculo rojo en el
  punto de click, que Sí/No funcionen, y que la acción (`click_at`/
  `type_text`/etc.) se ejecute después de confirmar.
- Probar con un caso controlado simple primero (ej. "hacé click en el
  botón X de esta ventana"), no con algo real todavía.
- Si se retoma en Windows: `core/screen_actions._capture_pyautogui()` es
  el path que se usaría ahí (nunca probado, solo el de `grim` en Linux).
  `core/mouse_actions.click_at`/`move_to` tampoco se probaron en Windows.
- El parseo JSON de la respuesta del modelo (`core/it_worker._extract_json`)
  es defensivo pero no se ejercitó con una respuesta real que pida una
  acción (`click`/`type`/etc.) — solo se probó una respuesta de texto
  libre (sin pedirle JSON) en el smoke test de la API.

---

Regla para retomar: pushear cada cambio terminado a `origin/main`, no
acumular (ver memoria `feedback-push-frequently`). Si pasó tiempo desde
la última sesión, correr `git fetch && git log main..origin/main` antes
de asumir que el local está al día (ver memoria `project-kanye`, sección
"Incidente de sync con git"). Dos checkouts del repo en esta máquina:
`/home/aaron/Documents/K.A.N.Y.E` (working dir de sesión) y
`/home/aaron/K.A.N.Y.E` (tiene el `.venv` con las deps instaladas) — hay
que mantener ambos sincronizados.
