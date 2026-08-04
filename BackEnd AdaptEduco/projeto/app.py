import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask

from config import Config
from database import db
from controllers.usuario_controller import usuario_bp

# Import models so SQLAlchemy registers the tables.
import models.usuario  # noqa: F401
import models.aluno  # noqa: F401
import models.professor  # noqa: F401
import models.responsavel  # noqa: F401
import models.turma  # noqa: F401
import models.conteudo  # noqa: F401
import models.atividade  # noqa: F401
import models.feedback  # noqa: F401
import models.relatorio  # noqa: F401
import models.adaptacao  # noqa: F401

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(usuario_bp)


@app.route("/")
def index():
    return "Aplicação rodando!"


with app.app_context():
    try:
        db.create_all()
    except Exception as exc:
        print(f"Aviso ao criar tabelas: {exc}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

