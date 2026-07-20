from controllers.crud_controller import criar_blueprint
from services.responsavel_service import responsavel_service

responsavel_bp = criar_blueprint("responsaveis", responsavel_service)
