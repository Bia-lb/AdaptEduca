from controllers.crud_controller import criar_blueprint
from services.conteudo_service import conteudo_service

conteudo_bp = criar_blueprint("conteudos", conteudo_service)
