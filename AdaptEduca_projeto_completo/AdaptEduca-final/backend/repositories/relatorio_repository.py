from models.relatorio import Relatorio
from repositories.base_repository import BaseRepository


class RelatorioRepository(BaseRepository):
    def __init__(self):
        super().__init__(Relatorio)


relatorio_repository = RelatorioRepository()
