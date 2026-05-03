from flask import Flask, request, jsonify

app = Flask("moods-service")

moods = []

def error_response(message, status_code=400):
    return jsonify({"status": "error", "message": message}), status_code

def success_response(data=None, message=None, status_code=200):
    response = {"status": "success"}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


@app.route('/mood', methods=['POST'])
def create_mood():
    payload = request.get_json(silent=True)

    if not payload:
        return error_response("Se requiere JSON")

    estado = payload.get("estado")
    usuario_id = payload.get("usuario_id")

    if not estado or not usuario_id:
        return error_response("estado y usuario_id son obligatorios")

    mood = {
        "id": len(moods) + 1,
        "usuario_id": usuario_id,
        "estado": estado
    }

    moods.append(mood)

    return success_response(mood, "Mood guardado", 201)


@app.route('/mood', methods=['GET'])
def list_moods():
    return success_response({
        "total": len(moods),
        "items": moods
    })


@app.route('/')
def health():
    return success_response(message="Servicio moods operativo")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)