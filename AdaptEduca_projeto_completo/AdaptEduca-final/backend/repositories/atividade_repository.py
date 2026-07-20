from models.atividade import Atividade
from repositories.base_repository import BaseRepository


class AtividadeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Atividade)


atividade_repository = AtividadeRepository()
