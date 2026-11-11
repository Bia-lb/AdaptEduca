
import os

from flask import jsonify
from app import create_app

env = os.getenv("FLASK_ENV", "development")

app = create_app(env)


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "Backend conectado com sucesso",
        "ambiente": env
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

