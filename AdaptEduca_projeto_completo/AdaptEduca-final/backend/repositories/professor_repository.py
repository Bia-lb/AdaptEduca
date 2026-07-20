from models.professor import Professor
from repositories.base_repository import BaseRepository


class ProfessorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Professor)


professor_repository = ProfessorRepository()
