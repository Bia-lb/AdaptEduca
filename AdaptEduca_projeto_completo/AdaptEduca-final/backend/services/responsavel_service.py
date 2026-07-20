from repositories.responsavel_repository import responsavel_repository
from services.base_service import BaseService


class ResponsavelService(BaseService):
    def __init__(self):
        super().__init__(responsavel_repository, ['usuario_id', 'parentesco', 'telefone'], ['usuario_id'], [])


responsavel_service = ResponsavelService()
