from models.adaptacao import Adaptacao
from repositories.base_repository import BaseRepository


class AdaptacaoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Adaptacao)


adaptacao_repository = AdaptacaoRepository()
