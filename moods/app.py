from flask import Flask, request, jsonify
import mysql.connector, os
from observability import get_logger, init_observability

app     = Flask(__name__)
logger  = get_logger("moods")
tracker = init_observability(app, "moods")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","db-moods"), user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""), database=os.getenv("DB_NAME","db_moods"),
        autocommit=True)

def serial(r):
    if r and r.get("creado_en"): r["creado_en"] = str(r["creado_en"])
    return r

@app.route("/mood", methods=["POST"])
def create_mood():
    p = request.get_json(silent=True) or {}
    estado, uid = p.get("estado"), p.get("usuario_id")
    if not all([estado, uid]):
        return jsonify({"error":"estado y usuario_id son obligatorios"}), 400
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO moods (usuario_id,estado) VALUES (%s,%s)", (uid, estado))
    mid = cur.lastrowid
    cur.execute("SELECT * FROM moods WHERE id=%s", (mid,))
    mood = serial(cur.fetchone()); cur.close(); conn.close()
    logger.info("Mood creado", extra={"usuario_id": uid})
    return jsonify({"status":"success","data":mood}), 201

@app.route("/mood", methods=["GET"])
def list_moods():
    uid = request.args.get("usuario_id")
    conn = get_db(); cur = conn.cursor(dictionary=True)
    if uid:
        cur.execute("SELECT * FROM moods WHERE usuario_id=%s ORDER BY creado_en DESC", (uid,))
    else:
        cur.execute("SELECT * FROM moods ORDER BY creado_en DESC")
    rows = [serial(r) for r in cur.fetchall()]; cur.close(); conn.close()
    return jsonify({"status":"success","data":{"total":len(rows),"items":rows}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
