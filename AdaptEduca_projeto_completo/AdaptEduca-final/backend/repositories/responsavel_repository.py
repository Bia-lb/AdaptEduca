from models.responsavel import Responsavel
from repositories.base_repository import BaseRepository


class ResponsavelRepository(BaseRepository):
    def __init__(self):
        super().__init__(Responsavel)


responsavel_repository = ResponsavelRepository()
