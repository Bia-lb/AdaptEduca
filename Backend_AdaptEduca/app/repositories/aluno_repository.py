from typing import Optional
from app.models.aluno import Aluno
from .base_repository import BaseRepository


class AlunoRepository(BaseRepository[Aluno]):
    def __init__(self) -> None:
        super().__init__(Aluno)

    def buscar_por_matricula(self, matricula: str) -> Optional[Aluno]:
        return Aluno.query.filter_by(matricula=matricula).first()
