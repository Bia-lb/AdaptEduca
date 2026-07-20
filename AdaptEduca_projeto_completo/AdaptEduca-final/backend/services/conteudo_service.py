from repositories.conteudo_repository import conteudo_repository
from services.base_service import BaseService


class ConteudoService(BaseService):
    def __init__(self):
        super().__init__(conteudo_repository, ['turma_id', 'titulo', 'tipo', 'arquivo', 'dataPostagem'], ['titulo'], ['dataPostagem'])


conteudo_service = ConteudoService()
