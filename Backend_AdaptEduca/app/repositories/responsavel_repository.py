from typing import List

from sqlalchemy import text
from app import db


class ResponsavelRepository:
    """Consultas SQL específicas de Responsável."""

    def listar_ids_por_turma(self, turma_id: int) -> List[int]:
        rows = db.session.execute(
            text("""
                SELECT rt.responsavel_id
                FROM responsavel_turma rt
                WHERE rt.turma_id = :turma_id
                ORDER BY rt.responsavel_id
            """),
            {"turma_id": turma_id},
        ).all()
        return [int(row[0]) for row in rows]
