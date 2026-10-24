from typing import List, Optional

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    def __init__(self) -> None:
        self.repo = UsuarioRepository()

    def listar(self) -> List[Usuario]:
        return Usuario.listar()

    def buscar(self, id: int) -> Optional[Usuario]:
        return Usuario.buscar_por_id(id)

    def email_disponivel(self, email: str) -> bool:
        return self.repo.buscar_id_por_email(email) is None

    def criar(self, dados: dict) -> Usuario:
        # Um Usuario "solto" não tem a linha de aluno/professor/responsável e
        # quebraria as consultas. O cadastro correto é /api/auth/register.
        raise ValueError("Use /api/auth/register para criar contas.")

    def atualizar(self, id: int, dados: dict) -> Usuario:

        usuario = Usuario.buscar_por_id(id)

        if not usuario:
            raise LookupError(
                f"Usuário {id} não encontrado."
            )

        novo_email = dados.get("email", usuario.email)
        if novo_email.lower() != usuario.email.lower() and not self.email_disponivel(novo_email):
            raise ValueError("E-mail já cadastrado.")
        return usuario.atualizar(
            nome=dados.get("nome", usuario.nome),
            email=novo_email,
            senha=dados.get("senha", usuario.senha)
        )

    def deletar(self, id: int) -> None:

        usuario = Usuario.buscar_por_id(id)

        if not usuario:
            raise LookupError(
                f"Usuário {id} não encontrado."
            )

        usuario.deletar()