from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import config

db = SQLAlchemy()


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[env])
    if hasattr(config[env], "validar"):
        config[env].validar()

    # Extensões
    db.init_app(app)

    # Permite que o frontend estático (ou outro host de desenvolvimento)
    # consuma a API REST.
    try:
        from flask_cors import CORS
        CORS(app, resources={r"/api/*": {"origins": "*"}},
             allow_headers=["Content-Type", "Authorization"])
    except ImportError:
        pass

    @app.get("/api/health")
    def health():
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            return {"sucesso": True, "mensagem": "API e MySQL conectados."}
        except Exception as exc:
            db.session.rollback()
            return {"sucesso": False, "mensagem": f"Falha na conexão com MySQL: {exc}"}, 500

    with app.app_context():
        # Importa modelos para que o SQLAlchemy os conheça
        from .models import usuario, aluno, professor, responsavel  # noqa: F401
        from .models import turma, conteudo, atividade              # noqa: F401
        from .models import adaptacao, feedback, relatorio, resposta, sessao_estudo, ia_uso  # noqa: F401

        # O schema do banco é criado pelo arquivo databasemodel.sql.
        # O SQLAlchemy é usado como camada ORM das Models, sem criar/alterar
        # tabelas automaticamente.

        # Rotas ativas (CRUD completo)
        from .routes.auth_routes import auth_bp
        from .routes.usuario_routes import usuario_bp
        from .routes.aluno_routes import aluno_bp
        from .routes.turma_routes import turma_bp
        from .routes.atividade_routes import atividade_bp
        from .routes.responsavel_routes import responsavel_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(usuario_bp)
        app.register_blueprint(aluno_bp)
        app.register_blueprint(turma_bp)
        app.register_blueprint(atividade_bp)
        app.register_blueprint(responsavel_bp)

        from .routes.conteudo_routes import conteudo_bp
        from .routes.estudo_routes import estudo_bp
        from .routes.feedback_routes import feedback_bp
        from .routes.progresso_routes import progresso_bp
        for bp in (conteudo_bp, estudo_bp, feedback_bp, progresso_bp):
            app.register_blueprint(bp)

        from .routes.ia_routes import ia_bp
        app.register_blueprint(ia_bp)

        # Rotas stub (entidades futuras)
        from .routes.stub_routes import stub_bp
        app.register_blueprint(stub_bp)

    return app
