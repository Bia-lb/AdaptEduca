from typing import Optional
from app.models.usuario import Usuario
from .base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self) -> None:
        super().__init__(Usuario)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        return Usuario.query.filter_by(email=email).first()
