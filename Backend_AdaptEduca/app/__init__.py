from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import config

db = SQLAlchemy()


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[env])

    # Extensões
    db.init_app(app)

    with app.app_context():
        # Importa modelos para que o SQLAlchemy os conheça
        from .models import usuario, aluno, professor, responsavel  # noqa: F401
        from .models import turma, conteudo, atividade              # noqa: F401
        from .models import adaptacao, feedback, relatorio           # noqa: F401

        db.create_all()

        # Rotas ativas (CRUD completo)
        from .routes.usuario_routes import usuario_bp
        from .routes.aluno_routes import aluno_bp
        from .routes.turma_routes import turma_bp
        from .routes.atividade_routes import atividade_bp
        from .routes.responsavel_routes import responsavel_bp

        app.register_blueprint(usuario_bp)
        app.register_blueprint(aluno_bp)
        app.register_blueprint(turma_bp)
        app.register_blueprint(atividade_bp)
        app.register_blueprint(responsavel_bp)

        # Rotas stub (entidades futuras)
        from .routes.stub_routes import stub_bp
        app.register_blueprint(stub_bp)

    return app
