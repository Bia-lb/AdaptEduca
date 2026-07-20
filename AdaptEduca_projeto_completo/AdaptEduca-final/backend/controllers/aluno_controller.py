from controllers.crud_controller import criar_blueprint
from services.aluno_service import aluno_service

aluno_bp = criar_blueprint("alunos", aluno_service)
