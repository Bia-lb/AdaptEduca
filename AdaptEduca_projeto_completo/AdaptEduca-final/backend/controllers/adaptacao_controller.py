from controllers.crud_controller import criar_blueprint
from services.adaptacao_service import adaptacao_service

adaptacao_bp = criar_blueprint("adaptacoes", adaptacao_service)
