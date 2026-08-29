from typing import List, Optional

from sqlalchemy import text
from app import db


class TurmaRepository:
    """Consultas SQL específicas de Turma."""

    def buscar_id_por_codigo(self, codigo: str) -> Optional[int]:
        row = db.session.execute(
            text("SELECT id FROM turma WHERE codigo = :codigo LIMIT 1"),
            {"codigo": codigo},
        ).first()
        return int(row[0]) if row else None

    def listar_ids_por_professor(self, professor_id: int) -> List[int]:
        rows = db.session.execute(
            text("SELECT id FROM turma WHERE professor_id = :professor_id ORDER BY nome, id"),
            {"professor_id": professor_id},
        ).all()
        return [int(row[0]) for row in rows]
