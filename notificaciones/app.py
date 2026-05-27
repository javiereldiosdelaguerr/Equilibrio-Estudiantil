from flask import Flask, request, jsonify
import mysql.connector
import os

from observability import get_logger, init_observability

app = Flask(__name__)

logger = get_logger("notificaciones")
tracker = init_observability(app, "notificaciones")


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db-notificaciones"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "db_notificaciones"),
        autocommit=True
    )


def serial(r):
    if r and r.get("creada_en"):
        r["creada_en"] = str(r["creada_en"])
    return r


@app.route("/notificaciones", methods=["GET", "POST"])
def crear():

    # GET -> para probar desde navegador
    if request.method == "GET":
        return jsonify({
            "status": "success",
            "message": "Servicio de notificaciones activo"
        }), 200

    # POST -> crear notificación
    p = request.get_json(silent=True) or {}

    uid = p.get("usuario_id")
    msg = p.get("mensaje")

    if not uid or not msg:
        return jsonify({
            "status": "error",
            "message": "usuario_id y mensaje son obligatorios"
        }), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "INSERT INTO notificaciones (usuario_id, mensaje) VALUES (%s, %s)",
        (uid, msg)
    )

    nid = cur.lastrowid

    cur.execute(
        "SELECT * FROM notificaciones WHERE id = %s",
        (nid,)
    )

    n = serial(cur.fetchone())

    cur.close()
    conn.close()

    logger.info(
        "Notificación creada",
        extra={"usuario_id": uid}
    )

    return jsonify({
        "status": "success",
        "data": n
    }), 201


@app.route("/notificaciones/<int:uid>", methods=["GET"])
def listar(uid):

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM notificaciones WHERE usuario_id = %s ORDER BY creada_en DESC",
        (uid,)
    )

    rows = [serial(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "total": len(rows),
            "items": rows
        }
    })


@app.route("/notificaciones/<int:nid>/leer", methods=["GET", "PUT"])
def leer(nid):

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "UPDATE notificaciones SET leida = TRUE WHERE id = %s",
        (nid,)
    )

    cur.execute(
        "SELECT * FROM notificaciones WHERE id = %s",
        (nid,)
    )

    n = serial(cur.fetchone())

    cur.close()
    conn.close()

    if not n:
        return jsonify({
            "status": "error",
            "message": "Notificación no encontrada"
        }), 404

    return jsonify({
        "status": "success",
        "data": n
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)