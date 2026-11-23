import os
import sqlite3
from datetime import date
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

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
    # Insertar usuario instructor por defecto si no existe
    # FALLO 2 (Contraseñas y hash): Contraseña en texto plano sin aplicar hash seguro
    cursor.execute("SELECT * FROM usuarios WHERE username = 'instructor'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES ('instructor', 'sena2024')")
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
        # Verificación directa de contraseña en texto plano (Fallo 2)
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
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

@app.route('/asistencia/registrar', methods=['POST'])
def registrar():
    if 'user' not in session:
        flash('No autorizado')
        return redirect(url_for('login'))

    aprendiz = request.form.get('aprendiz')
    ficha = request.form.get('ficha')
    fecha = request.form.get('fecha')
    estado = request.form.get('estado')

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

# FALLO 3 (Control de acceso): Endpoint de eliminación no valida sesión de instructor
@app.route('/asistencia/eliminar/<int:id>')
def eliminar(id):
    fecha = request.args.get('fecha', date.today().isoformat())
    # NOTA: No se verifica `if 'user' not in session:` permitiendo acceso no autenticado
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

