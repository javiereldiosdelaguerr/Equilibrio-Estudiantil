from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

USUARIOS_URL = "http://usuarios:5001"
MOODS_URL = "http://moods:5002"
SESIONES_URL = "http://sesiones:5003"
RECOMENDACIONES_URL = "http://recomendaciones:5004"


@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    try:
        if request.method == "GET":
            res = requests.get(f"{USUARIOS_URL}/usuarios", timeout=5)
        else:
            res = requests.post(f"{USUARIOS_URL}/usuarios", json=request.json, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/mood", methods=["GET", "POST"])
def mood():
    try:
        if request.method == "GET":
            res = requests.get(f"{MOODS_URL}/mood", timeout=5)
        else:
            res = requests.post(f"{MOODS_URL}/mood", json=request.json, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recomendacion/<int:id>")
def recomendacion(id):
    res = requests.get(f"{RECOMENDACIONES_URL}/recomendacion/{id}")
    return jsonify(res.json()), res.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)