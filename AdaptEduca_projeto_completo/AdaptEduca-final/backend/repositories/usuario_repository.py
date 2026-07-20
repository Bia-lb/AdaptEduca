from models.usuario import Usuario
from repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    def __init__(self):
        super().__init__(Usuario)

    def buscar_por_email(self, email):
        return Usuario.query.filter_by(email=email).first()


usuario_repository = UsuarioRepository()
