from models.turma import Turma
from repositories.base_repository import BaseRepository


class TurmaRepository(BaseRepository):
    def __init__(self):
        super().__init__(Turma)


turma_repository = TurmaRepository()
