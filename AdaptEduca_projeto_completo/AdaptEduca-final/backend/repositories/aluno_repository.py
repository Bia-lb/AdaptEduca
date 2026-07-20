from models.aluno import Aluno
from repositories.base_repository import BaseRepository


class AlunoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Aluno)


aluno_repository = AlunoRepository()
