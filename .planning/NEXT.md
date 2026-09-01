# Próximos pasos — K.A.N.Y.E.

Estado al momento de escribir esto: loop agéntico (`core/agent.py` +
`core/tools.py`) y rediseño de GUI mono (`core/theme.py`) ya están en
`main`, pusheados. Tools incluyen control de mouse (`mouse_move/click/
scroll/drag`). Todo probado con mocks, **no probado todavía contra un
modelo real corriendo**.

## 1. Probar el loop agéntico con un modelo real (primero)

Reiniciar K.A.N.Y.E. (`python3 main.py` o el lanzador que uses) y probar
en vivo, no con mocks:
- Un comando simple: `abrí firefox`
- Encadenado: `cerrá spotify y abrí firefox y buscá el clima`
- Algo con mouse: `movete el mouse a la derecha y hacé click`
- Chat puro sin tools: una pregunta de opinión
- Ver si `phi4-mini` (default de `chat_model`) sostiene bien el
  tool-calling multi-paso, o si hace falta subir a `qwen2.5:7b` (ya
  documentado como alternativa en el README) o usar DeepSeek como backend
  principal si hay API key.

## 2. Más tools candidatas (a definir cuáles priorizar)

- **Screenshot / captura de pantalla**: le daría al agente algo de
  "visión" — hoy el mouse es ciego (solo direcciones relativas, no puede
  apuntar a un botón específico en pantalla). Requeriría además mandarle
  la imagen a un modelo con visión (DeepSeek/Ollama con soporte
  multimodal), no es trivial — evaluar si vale la pena.
- **Control de ventanas**: minimizar/maximizar/cambiar de escritorio,
  aparte de lo que ya hace `close_all_desktop_apps` en `process_actions.py`.
- **Notas/memoria persistente**: algo tipo "recordá esto" que sobreviva
  fuera del historial de chat (`config/history.json` ya se trunca a los
  últimos 24 mensajes).

## 3. Pulir la GUI mono una vez se vea corriendo de verdad

El rediseño (blanco/negro, sin dorado) se verificó con capturas de un
proceso de prueba, pero no en el uso real día a día. Cosas a revisar con
ojo fresco:
- El chip de estado y el borde del botón CTA con blanco en vez de dorado
  — puede que necesiten más contraste o un tono ligeramente distinto de
  `theme.ACCENT` (`#FFFFFF`) para no verse "plano".
- Confirmar que Win+C ahora minimiza en vez de matar el proceso (fix ya
  pusheado, sin probar en vivo).

---

Regla para retomar: pushear cada cambio terminado a `origin/main`, no
acumular (ver memoria `feedback-push-frequently`). Si pasó tiempo desde
la última sesión, correr `git fetch && git log main..origin/main` antes
de asumir que el local está al día (ver memoria `project-kanye`, sección
"Incidente de sync con git").
