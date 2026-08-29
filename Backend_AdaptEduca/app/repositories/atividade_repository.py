from typing import List

from sqlalchemy import text
from app import db


class AtividadeRepository:
    """Consultas SQL específicas de Atividade."""

    def listar_ids_por_turma(self, turma_id: int) -> List[int]:
        rows = db.session.execute(
            text("SELECT id FROM atividade WHERE turma_id = :turma_id ORDER BY prazo, id"),
            {"turma_id": turma_id},
        ).all()
        return [int(row[0]) for row in rows]

    def listar_ids_por_status(self, status: str) -> List[int]:
        rows = db.session.execute(
            text("SELECT id FROM atividade WHERE status = :status ORDER BY prazo, id"),
            {"status": status},
        ).all()
        return [int(row[0]) for row in rows]
