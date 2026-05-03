from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

sesiones = []
current_id = 1


@app.route("/sesiones", methods=["POST"])
def crear_sesion():
    global current_id

    data = request.json

    if not data or "usuario_id" not in data:
        return jsonify({"error": "Falta usuario_id"}), 400

    sesion = {
        "id": current_id,
        "usuario_id": data["usuario_id"],
        "duracion": data.get("duracion", 25),
        "estado": "activa",
        "inicio": datetime.utcnow().isoformat()
    }

    sesiones.append(sesion)
    current_id += 1

    return jsonify(sesion), 201


@app.route("/sesiones", methods=["GET"])
def listar_sesiones():
    return jsonify(sesiones)


@app.route("/sesiones/<int:id>/finalizar", methods=["PUT"])
def finalizar_sesion(id):
    for s in sesiones:
        if s["id"] == id:
            s["estado"] = "finalizada"
            s["fin"] = datetime.utcnow().isoformat()
            return jsonify(s)

    return jsonify({"error": "Sesion no encontrada"}), 404


@app.route("/")
def home():
    return "Servicio sesiones funcionando"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)