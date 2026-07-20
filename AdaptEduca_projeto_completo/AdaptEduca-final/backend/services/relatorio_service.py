from repositories.relatorio_repository import relatorio_repository
from services.base_service import BaseService


class RelatorioService(BaseService):
    def __init__(self):
        super().__init__(relatorio_repository, ['aluno_id', 'desempenho', 'tempoEstudo', 'materiasDificeis', 'periodo'], [], [])


relatorio_service = RelatorioService()
