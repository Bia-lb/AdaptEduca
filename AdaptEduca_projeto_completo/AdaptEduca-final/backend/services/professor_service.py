from repositories.professor_repository import professor_repository
from services.base_service import BaseService


class ProfessorService(BaseService):
    def __init__(self):
        super().__init__(professor_repository, ['usuario_id', 'formacao', 'disciplina'], ['usuario_id'], [])


professor_service = ProfessorService()
