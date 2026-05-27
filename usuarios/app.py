from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector, os
from observability import get_logger, init_observability

app     = Flask(__name__)
logger  = get_logger("usuarios")
tracker = init_observability(app, "usuarios")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","db-usuarios"), user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""), database=os.getenv("DB_NAME","db_usuarios"),
        autocommit=True)

def ok(data=None, msg=None, code=200):
    r = {"status":"success"}
    if msg:  r["message"] = msg
    if data is not None: r["data"] = data
    return jsonify(r), code

def err(msg, code=400):
    return jsonify({"status":"error","message":msg}), code

@app.route("/usuarios", methods=["POST"])
def create_user():
    p = request.get_json(silent=True) or {}
    nombre, email, password = p.get("nombre"), p.get("email"), p.get("password")
    if not all([nombre, email, password]):
        return err("nombre, email y password son obligatorios")
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
        if cur.fetchone(): return err("Email ya registrado", 409)
        cur.execute("INSERT INTO usuarios (nombre,email,password,fecha_creacion) VALUES (%s,%s,%s,%s)",
                    (nombre, email, password, datetime.utcnow()))
        uid = cur.lastrowid
        cur.execute("SELECT id,nombre,email FROM usuarios WHERE id=%s", (uid,))
        logger.info("Usuario creado", extra={"usuario_id": uid})
        return ok(cur.fetchone(), "Usuario creado", 201)
    except Exception as e:
        logger.error(str(e)); return err("Error interno", 500)
    finally: cur.close(); conn.close()

@app.route("/login", methods=["POST"])
def login():
    p = request.get_json(silent=True) or {}
    email, password = p.get("email"), p.get("password")
    if not all([email, password]): return err("email y password son obligatorios")
    conn = get_db(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        u = cur.fetchone()
        if not u: return err("Usuario no encontrado", 404)
        if u["password"] != password: return err("Contraseña incorrecta", 401)
        u.pop("password", None)
        if u.get("fecha_creacion"): u["fecha_creacion"] = str(u["fecha_creacion"])
        logger.info("Login exitoso", extra={"usuario_id": u["id"]})
        return ok(u, "Login exitoso")
    finally: cur.close(); conn.close()

@app.route("/usuarios", methods=["GET"])
def list_users():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id,nombre,email FROM usuarios")
    rows = cur.fetchall(); cur.close(); conn.close()
    return ok({"total": len(rows), "items": rows})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
