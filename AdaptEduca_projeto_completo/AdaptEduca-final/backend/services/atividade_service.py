from repositories.atividade_repository import atividade_repository
from services.base_service import BaseService


class AtividadeService(BaseService):
    def __init__(self):
        super().__init__(atividade_repository, ['turma_id', 'conteudo_id', 'titulo', 'descricao', 'prazo', 'status'], ['titulo'], ['prazo'])


atividade_service = AtividadeService()
