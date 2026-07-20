from controllers.crud_controller import criar_blueprint
from services.atividade_service import atividade_service

atividade_bp = criar_blueprint("atividades", atividade_service)
