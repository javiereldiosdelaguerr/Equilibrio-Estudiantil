from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector, os
from observability import get_logger, init_observability

app     = Flask(__name__)
logger  = get_logger("sesiones")
tracker = init_observability(app, "sesiones")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","db-sesiones"), user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""), database=os.getenv("DB_NAME","db_sesiones"),
        autocommit=True)

def serial(r):
    for k in ("inicio","fin"):
        if r and r.get(k): r[k] = str(r[k])
    return r

@app.route("/sesiones", methods=["POST"])
def crear():
    p = request.get_json(silent=True) or {}
    uid = p.get("usuario_id")
    if not uid: return jsonify({"error":"Falta usuario_id"}), 400
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO sesiones (usuario_id,duracion) VALUES (%s,%s)", (uid, p.get("duracion",25)))
    sid = cur.lastrowid
    cur.execute("SELECT * FROM sesiones WHERE id=%s", (sid,))
    s = serial(cur.fetchone()); cur.close(); conn.close()
    logger.info("Sesión creada", extra={"usuario_id": uid})
    return jsonify({"status":"success","data":s}), 201

@app.route("/sesiones", methods=["GET"])
def listar():
    uid = request.args.get("usuario_id")
    conn = get_db(); cur = conn.cursor(dictionary=True)
    if uid:
        cur.execute("SELECT * FROM sesiones WHERE usuario_id=%s ORDER BY inicio DESC", (uid,))
    else:
        cur.execute("SELECT * FROM sesiones ORDER BY inicio DESC")
    rows = [serial(r) for r in cur.fetchall()]; cur.close(); conn.close()
    return jsonify({"status":"success","data":{"items":rows}})

@app.route("/sesiones/<int:id>/finalizar", methods=["PUT"])
def finalizar(id):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM sesiones WHERE id=%s", (id,))
    s = cur.fetchone()
    if not s: cur.close(); conn.close(); return jsonify({"error":"No encontrada"}), 404
    cur.execute("UPDATE sesiones SET estado='finalizada',fin=%s WHERE id=%s", (datetime.utcnow(), id))
    cur.execute("SELECT * FROM sesiones WHERE id=%s", (id,))
    s = serial(cur.fetchone()); cur.close(); conn.close()
    return jsonify({"status":"success","data":s})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
