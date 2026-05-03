from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)


def get_db():
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        autocommit=True
    )


def error_response(message, status_code=400):
    return jsonify({"status": "error", "message": message}), status_code


def success_response(data=None, message=None, status_code=200):
    response = {"status": "success"}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


@app.route('/usuarios', methods=['POST'])
def create_user():
    payload = request.get_json(silent=True)

    if not payload:
        return error_response("Se requiere JSON")

    nombre = payload.get("nombre")
    email = payload.get("email")
    password = payload.get("password")

    if not nombre or not email or not password:
        return error_response("nombre, email y password son obligatorios")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return error_response("Email ya registrado", 409)

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, fecha_creacion) VALUES (%s, %s, %s, %s)",
            (nombre, email, password, datetime.utcnow())
        )
        conn.commit()

        user_id = cursor.lastrowid
        cursor.execute("SELECT id, nombre, email FROM usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        return success_response(user, "Usuario creado", 201)

    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True)

    if not payload:
        return error_response("Se requiere JSON")

    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return error_response("email y password son obligatorios")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return error_response("Usuario no encontrado", 404)

        if user["password"] != password:
            return error_response("Contraseña incorrecta", 401)

        user.pop("password", None)

        return success_response(user, "Login exitoso")

    finally:
        cursor.close()
        conn.close()


@app.route('/usuarios', methods=['GET'])
def list_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, email FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return success_response({"total": len(usuarios), "items": usuarios})


@app.route('/', methods=['GET'])
def health():
    return success_response(message="Servicio usuarios OK")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)