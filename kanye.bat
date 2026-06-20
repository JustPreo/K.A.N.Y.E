@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Primera vez: creando entorno virtual...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
)

call .venv\Scripts\activate
python main.py %*
