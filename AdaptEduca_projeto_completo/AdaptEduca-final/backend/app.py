import os
from flask import Flask, jsonify, send_from_directory
from config import Config
from database import db
from models import Usuario, Professor, Aluno, Responsavel, Turma, Conteudo, Atividade, Adaptacao, Feedback, Relatorio
from controllers import blueprints

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.config.from_object(Config)
db.init_app(app)

for blueprint in blueprints:
    app.register_blueprint(blueprint)


@app.get("/")
def pagina_inicial():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "projeto": "AdaptEduca"})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
