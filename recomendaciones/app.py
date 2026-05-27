from flask import Flask, jsonify
import mysql.connector, requests as req, os
from observability import get_logger, init_observability, CircuitBreaker, CircuitOpenError

app     = Flask(__name__)
logger  = get_logger("recomendaciones")
tracker = init_observability(app, "recomendaciones")

cb_moods    = CircuitBreaker("moods",    failure_threshold=3, recovery_timeout=30, logger=logger)
cb_sesiones = CircuitBreaker("sesiones", failure_threshold=3, recovery_timeout=30, logger=logger)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","db-recomendaciones"), user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""), database=os.getenv("DB_NAME","db_recomendaciones"),
        autocommit=True)

def fetch(cb, url):
    try:
        r = cb.call(req.get, url, timeout=5)
        return r.json().get("data",{}).get("items",[])
    except (CircuitOpenError, Exception) as e:
        logger.warning(str(e), extra={"circuit": cb.name})
        return []

@app.route("/recomendacion/<int:uid>")
def recomendar(uid):
    moods    = fetch(cb_moods,    f"http://moods:5002/mood?usuario_id={uid}")
    sesiones = fetch(cb_sesiones, f"http://sesiones:5003/sesiones?usuario_id={uid}")

    estado = moods[0]["estado"] if moods else None
    texto  = {"estresado": "Toma un descanso de 10 minutos",
               "normal":    "Puedes continuar estudiando",
               "feliz":     "Aprovecha tu energía para avanzar más"}.get(estado, "Registra tu estado de ánimo")
    if len(sesiones) >= 4:
        texto = "Has trabajado mucho hoy, descansa"

    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO recomendaciones (usuario_id,estado_mood,total_sesiones,recomendacion) VALUES (%s,%s,%s,%s)",
                    (uid, estado, len(sesiones), texto))
        cur.close(); conn.close()
    except Exception as e:
        logger.error(str(e))

    logger.info("Recomendación generada", extra={"usuario_id": uid})
    return jsonify({"usuario_id":uid,"estado":estado,"sesiones":len(sesiones),"recomendacion":texto})

@app.route("/recomendaciones/<int:uid>")
def historial(uid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM recomendaciones WHERE usuario_id=%s ORDER BY generada_en DESC", (uid,))
    rows = cur.fetchall()
    for r in rows:
        if r.get("generada_en"): r["generada_en"] = str(r["generada_en"])
    cur.close(); conn.close()
    return jsonify({"status":"success","data":{"items":rows}})

@app.route("/circuits")
def circuits():
    return jsonify([cb_moods.status(), cb_sesiones.status()])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
