from typing import Optional

from sqlalchemy import text

from app import db


class UsuarioRepository:
    """Consultas SQL específicas de Usuario."""

    def buscar_id_por_email(self, email: str) -> Optional[int]:
        row = db.session.execute(
            text(
                """
                SELECT id
                FROM usuario
                WHERE LOWER(email) = LOWER(:email)
                LIMIT 1
                """
            ),
            {"email": email}
        ).first()

        return int(row[0]) if row else None