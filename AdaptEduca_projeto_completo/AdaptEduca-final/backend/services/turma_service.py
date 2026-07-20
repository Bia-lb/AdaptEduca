from repositories.turma_repository import turma_repository
from services.base_service import BaseService


class TurmaService(BaseService):
    def __init__(self):
        super().__init__(turma_repository, ['codigo', 'nome', 'descricao', 'professor_id', 'responsavel_id'], ['codigo', 'nome'], [])


turma_service = TurmaService()
