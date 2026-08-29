import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from app import create_app


env = os.getenv("FLASK_ENV", "development")

app = create_app(env)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "Backend conectado com sucesso",
        "ambiente": env
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=(env == "development")
    )