from controllers.crud_controller import criar_blueprint
from services.turma_service import turma_service

turma_bp = criar_blueprint("turmas", turma_service)
