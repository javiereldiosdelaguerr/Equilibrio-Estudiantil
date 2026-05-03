from flask import Flask, jsonify
import requests

app = Flask(__name__)

MOODS_URL = "http://moods:5002"
SESIONES_URL = "http://sesiones:5003"


@app.route("/")
def home():
    return "Servicio recomendaciones funcionando"


@app.route("/recomendacion/<int:usuario_id>", methods=["GET"])
def recomendar(usuario_id):
    try:
        mood_res = requests.get(f"{MOODS_URL}/mood", timeout=5)
        moods_data = mood_res.json().get("data", {}).get("items", [])

        ses_res = requests.get(f"{SESIONES_URL}/sesiones", timeout=5)
        sesiones_data = ses_res.json().get("data", {}).get("items", [])

        ultimo_estado = None
        sesiones_usuario = []

        for m in moods_data:
            if m["usuario_id"] == usuario_id:
                ultimo_estado = m["estado"]

        for s in sesiones_data:
            if s["usuario_id"] == usuario_id:
                sesiones_usuario.append(s)

        if ultimo_estado == "estresado":
            recomendacion = "Toma un descanso de 10 minutos"
        elif ultimo_estado == "normal":
            recomendacion = "Puedes continuar estudiando"
        elif ultimo_estado == "feliz":
            recomendacion = "Aprovecha tu energía para avanzar más"
        else:
            recomendacion = "Registra tu estado de ánimo"

        if len(sesiones_usuario) >= 4:
            recomendacion = "Has trabajado mucho, descansa un poco"

        return jsonify({
            "usuario_id": usuario_id,
            "estado": ultimo_estado,
            "sesiones": len(sesiones_usuario),
            "recomendacion": recomendacion
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "No se pudo generar la recomendación",
            "detalle": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)