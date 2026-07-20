from repositories.aluno_repository import aluno_repository
from services.base_service import BaseService


class AlunoService(BaseService):
    def __init__(self):
        super().__init__(aluno_repository, ['usuario_id', 'matricula', 'preferenciaAprendizagem', 'progresso', 'dataNascimento'], ['usuario_id', 'matricula'], ['dataNascimento'])


aluno_service = AlunoService()
