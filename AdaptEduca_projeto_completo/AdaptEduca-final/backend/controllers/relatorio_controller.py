from controllers.crud_controller import criar_blueprint
from services.relatorio_service import relatorio_service

relatorio_bp = criar_blueprint("relatorios", relatorio_service)
