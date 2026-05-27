from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as req

from observability import get_logger, init_observability, CircuitBreaker, CircuitOpenError

app = Flask(__name__)
CORS(app)

logger = get_logger("gateway")
tracker = init_observability(app, "gateway")

URLS = {
    "usuarios":        "http://usuarios:5001",
    "moods":           "http://moods:5002",
    "sesiones":        "http://sesiones:5003",
    "recomendaciones": "http://recomendaciones:5004",
    "notificaciones":  "http://notificaciones:5005",
}

CB = {
    k: CircuitBreaker(
        k,
        failure_threshold=3,
        recovery_timeout=30,
        logger=logger
    )
    for k in URLS
}


def proxy(service, method, path, **kwargs):
    cb = CB[service]

    try:
        fn = getattr(req, method)

        res = cb.call(
            fn,
            f"{URLS[service]}{path}",
            timeout=5,
            **kwargs
        )

        return jsonify(res.json()), res.status_code

    except CircuitOpenError:
        return jsonify({
            "error": f"Servicio {service} no disponible temporalmente"
        }), 503

    except Exception as e:
        logger.error(str(e), extra={"error": str(e)})

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/")
def home():
    return jsonify({
        "mensaje": "Gateway funcionando correctamente",
        "servicios": list(URLS.keys())
    })


@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():

    if request.method == "GET":
        return proxy("usuarios", "get", "/usuarios")

    return proxy(
        "usuarios",
        "post",
        "/usuarios",
        json=request.json
    )


@app.route("/login", methods=["POST"])
def login():
    return proxy(
        "usuarios",
        "post",
        "/login",
        json=request.json
    )


@app.route("/mood", methods=["GET", "POST"])
def mood():

    if request.method == "GET":
        return proxy(
            "moods",
            "get",
            "/mood",
            params=request.args
        )

    return proxy(
        "moods",
        "post",
        "/mood",
        json=request.json
    )


@app.route("/sesiones", methods=["GET", "POST"])
def sesiones():

    if request.method == "GET":
        return proxy(
            "sesiones",
            "get",
            "/sesiones",
            params=request.args
        )

    return proxy(
        "sesiones",
        "post",
        "/sesiones",
        json=request.json
    )


@app.route("/sesiones/<int:id>/finalizar", methods=["PUT"])
def finalizar(id):
    return proxy(
        "sesiones",
        "put",
        f"/sesiones/{id}/finalizar"
    )


@app.route("/recomendacion/<int:id>")
def recomendacion(id):
    return proxy(
        "recomendaciones",
        "get",
        f"/recomendacion/{id}"
    )


@app.route("/notificaciones", methods=["POST"])
def crear_notif():
    return proxy(
        "notificaciones",
        "post",
        "/notificaciones",
        json=request.json
    )


@app.route("/notificaciones/<int:uid>")
def listar_notif(uid):
    return proxy(
        "notificaciones",
        "get",
        f"/notificaciones/{uid}"
    )


@app.route("/circuits")
def circuits():
    return jsonify([cb.status() for cb in CB.values()])


@app.route("/estado/<string:servicio>")
def estado_servicio(servicio):

    if servicio not in URLS:
        return jsonify({
            "error": "Servicio no encontrado"
        }), 404

    try:
        res = req.get(
            f"{URLS[servicio]}/health",
            timeout=3
        )

        return jsonify(res.json()), res.status_code

    except Exception:
        return jsonify({
            "service": servicio,
            "status": "down"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)