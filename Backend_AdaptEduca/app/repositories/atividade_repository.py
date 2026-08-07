from typing import List
from app.models.atividade import Atividade
from .base_repository import BaseRepository


class AtividadeRepository(BaseRepository[Atividade]):
    def __init__(self) -> None:
        super().__init__(Atividade)

    def listar_por_turma(self, turma_id: int) -> List[Atividade]:
        return Atividade.query.filter_by(turma_id=turma_id).all()

    def listar_por_status(self, status: str) -> List[Atividade]:
        return Atividade.query.filter_by(status=status).all()
