import os
import sqlite3
from datetime import date
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

# Cargar variables de entorno desde archivo .env local
load_dotenv()

# Configuración básica de templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Clave de sesión extraída de variables de entorno (Criterio 4: Secretos y claves)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_insegura_solo_para_tests")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'asistencia.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # Tabla de instructores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Tabla de asistencias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aprendiz TEXT NOT NULL,
            ficha TEXT NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')
    # Insertar usuario instructor por defecto si no existe (con hash seguro)
    cursor.execute("SELECT * FROM usuarios WHERE username = 'instructor'")
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            ('instructor', generate_password_hash('sena2024'))
        )
    elif not user['password'].startswith(('scrypt:', 'pbkdf2:')):
        # Migración a hash si existe contraseña previa en texto plano
        cursor.execute(
            "UPDATE usuarios SET password = ? WHERE username = 'instructor'",
            (generate_password_hash('sena2024'),)
        )
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('asistencia'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        # Verificación segura mediante hash criptográfico (Criterio 3: Contraseñas y hash)
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            flash('Inicio de sesión exitoso')
            return redirect(url_for('asistencia'))
        else:
            flash('Credenciales incorrectas')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Sesión cerrada correctamente')
    return redirect(url_for('login'))

@app.route('/asistencia')
def asistencia():
    if 'user' not in session:
        flash('Debe iniciar sesión para acceder')
        return redirect(url_for('login'))

    fecha = request.args.get('fecha', date.today().isoformat())
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM asistencias WHERE fecha = ?", (fecha,))
    registros = cursor.fetchall()
    conn.close()
    return render_template('asistencia.html', asistencias=registros, fecha_filtro=fecha)

ESTADOS_VALIDOS = {'Presente', 'Ausente', 'Excusa'}

@app.route('/asistencia/registrar', methods=['POST'])
def registrar():
    if 'user' not in session:
        flash('No autorizado')
        return redirect(url_for('login'))

    aprendiz = (request.form.get('aprendiz') or '').strip()
    ficha = (request.form.get('ficha') or '').strip()
    fecha = request.form.get('fecha') or date.today().isoformat()
    estado = request.form.get('estado')

    # Validación estricta de entradas (Criterio 2: Validación de entradas)
    if not aprendiz or not ficha or estado not in ESTADOS_VALIDOS:
        flash('Datos de asistencia inválidos o incompletos')
        return redirect(url_for('asistencia', fecha=fecha))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO asistencias (aprendiz, ficha, fecha, estado) VALUES (?, ?, ?, ?)",
        (aprendiz, ficha, fecha, estado)
    )
    conn.commit()
    conn.close()
    flash('Asistencia registrada correctamente')
    return redirect(url_for('asistencia', fecha=fecha))

# Corrección Fallo 1 (Criterio 5 - Control de acceso): Validar sesión activa de instructor
@app.route('/asistencia/eliminar/<int:id>')
def eliminar(id):
    if 'user' not in session:
        flash('Debe iniciar sesión para realizar esta acción')
        return redirect(url_for('login'))

    fecha = request.args.get('fecha', date.today().isoformat())
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asistencias WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Registro eliminado')
    return redirect(url_for('asistencia', fecha=fecha))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

