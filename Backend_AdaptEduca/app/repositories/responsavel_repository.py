from typing import List
from app.models.responsavel import Responsavel
from .base_repository import BaseRepository


class ResponsavelRepository(BaseRepository[Responsavel]):
    def __init__(self) -> None:
        super().__init__(Responsavel)

    def listar_por_turma(self, turma_id: int) -> List[Responsavel]:
        return (
            Responsavel.query
            .filter(Responsavel.turmas.any(id=turma_id))
            .all()
        )
