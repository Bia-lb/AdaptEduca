from models.conteudo import Conteudo
from repositories.base_repository import BaseRepository


class ConteudoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Conteudo)


conteudo_repository = ConteudoRepository()
