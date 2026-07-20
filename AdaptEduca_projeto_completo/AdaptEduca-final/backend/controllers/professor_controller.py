from controllers.crud_controller import criar_blueprint
from services.professor_service import professor_service

professor_bp = criar_blueprint("professores", professor_service)
