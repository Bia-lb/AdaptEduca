from typing import Optional
from sqlalchemy import text
from app import db


class AlunoRepository:
    """Consultas SQL específicas de Aluno."""

    def buscar_id_por_matricula(self, matricula: str) -> Optional[int]:
        row = db.session.execute(
            text("SELECT id FROM aluno WHERE matricula = :matricula LIMIT 1"),
            {"matricula": matricula},
        ).first()
        return int(row[0]) if row else None
