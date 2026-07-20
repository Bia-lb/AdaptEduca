from repositories.adaptacao_repository import adaptacao_repository
from services.base_service import BaseService


class AdaptacaoService(BaseService):
    def __init__(self):
        super().__init__(adaptacao_repository, ['conteudo_id', 'modo', 'resumo', 'audio', 'mapaMental'], [], [])


adaptacao_service = AdaptacaoService()
