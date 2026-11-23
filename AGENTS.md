# Contexto para Agentes de IA - Control de Asistencia

## Proyecto
Sistema web para registrar, consultar, editar y eliminar asistencia de aprendices por fecha (SENA), con autenticación exclusiva de instructores.

## Stack
- Python 3.10+, Flask 3.x, SQLite3, Jinja2, python-dotenv.
- Testing y Calidad: Pytest, Ruff, Pre-commit.

## Comandos
- Entorno: `python -m venv .venv && source .venv/bin/activate` (o `.venv\Scripts\activate`)
- Instalar dependencias: `pip install -r requirements.txt`
- Ejecutar: `python app/main.py`
- Pruebas: `pytest tests/`
- Linter: `ruff check .` / Formato: `ruff format .`

## Estructura
- `app/`: Lógica de la aplicación y base de datos (`main.py`).
- `templates/`: Plantillas HTML (`base.html`, `login.html`, `asistencia.html`).
- `tests/`: Pruebas de humo (`test_humo.py`) y pruebas de regresión (`test_fallos.py`).
- Archivos raíz: `.env.example`, `.gitignore`, `pyproject.toml`, `requirements.txt`.

## Qué no hacer
- NUNCA quemar secretos, tokens o contraseñas en el código fuente.
- NO subir `.env`, bases de datos SQLite (`*.db`) ni `.venv` a Git.
- NO omitir validaciones de sesión en endpoints de modificación o eliminación.
- NO almacenar contraseñas en texto plano; usar siempre hashing seguro.

## Lecciones aprendidas
- Todo endpoint que mute o elimine datos debe verificar la sesión activa del instructor antes de tocar la BD.

