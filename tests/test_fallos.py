import pytest
from app.main import app, get_db, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_fallo_1_eliminar_sin_autenticacion_rechazado(client):
    """
    FALLO 1 (Criterio 5 - Control de acceso):
    Un usuario anónimo NO debe poder eliminar registros de asistencia.
    Debe redirigir al login y el registro debe permanecer en la BD.
    """
    # 1. Insertamos un registro de asistencia previo
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO asistencias (aprendiz, ficha, fecha, estado) VALUES (?, ?, ?, ?)",
        ("Carlos Gómez", "2670123", "2026-11-23", "Presente")
    )
    reg_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 2. Intento de eliminación sin sesión activa (usuario no autenticado)
    response = client.get(f"/asistencia/eliminar/{reg_id}", follow_redirects=False)

    # 3. Verificamos que se exija login
    assert response.status_code == 302, f"Esperado 302, pero se obtuvo {response.status_code}"
    assert "/login" in response.headers.get("Location", "")

    # 4. Verificamos que el registro siga existiendo en la base de datos
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM asistencias WHERE id = ?", (reg_id,))
    registro = cursor.fetchone()
    conn.close()
    assert registro is not None, "VULNERABILIDAD: El registro fue eliminado sin sesión activa"

def test_fallo_2_contrasenas_con_hash_seguro():
    """
    FALLO 2 (Criterio 3 - Contraseñas y hash):
    Las contraseñas de los usuarios no deben almacenarse en texto plano.
    Deben usar un hash seguro de werkzeug.security (scrypt o pbkdf2)
    y no coincidir con la contraseña en texto plano original.
    """
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE username = 'instructor'")
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "El usuario instructor debe existir"
    stored_password = row['password']

    # La contraseña en base de datos NO debe ser texto plano
    assert stored_password != "sena2024", "VULNERABILIDAD: La contraseña se almacena en texto plano"

    # La contraseña debe tener el formato de un hash criptográfico de Werkzeug
    assert stored_password.startswith(("scrypt:", "pbkdf2:sha256:")), (
        f"La contraseña no tiene formato de hash seguro válido: {stored_password}"
    )
