from typing import Optional, List
from app.models.turma import Turma
from .base_repository import BaseRepository


class TurmaRepository(BaseRepository[Turma]):
    def __init__(self) -> None:
        super().__init__(Turma)

    def buscar_por_codigo(self, codigo: str) -> Optional[Turma]:
        return Turma.query.filter_by(codigo=codigo).first()

    def listar_por_professor(self, professor_id: int) -> List[Turma]:
        return Turma.query.filter_by(professor_id=professor_id).all()
