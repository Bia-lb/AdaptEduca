from typing import List, Optional
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    """
    Regras de negócio para Usuario.
    Decisão técnica: senhas armazenadas em texto plano nesta fase.
    Adicionar werkzeug.security.generate_password_hash em produção.
    """

    def __init__(self) -> None:
        self._repo = UsuarioRepository()

    def listar(self) -> List[Usuario]:
        return self._repo.listar_todos()

    def buscar(self, id: int) -> Optional[Usuario]:
        return self._repo.buscar_por_id(id)

    def criar(self, dados: dict) -> Usuario:
        if self._repo.buscar_por_email(dados["email"]):
            raise ValueError(f"E-mail {dados['email']!r} já cadastrado.")

        usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            tipoPerfil=dados["tipoPerfil"],
        )
        return self._repo.salvar(usuario)

    def atualizar(self, id: int, dados: dict) -> Usuario:
        usuario = self._repo.buscar_por_id(id)
        if not usuario:
            raise LookupError(f"Usuário {id} não encontrado.")

        usuario.nome = dados.get("nome", usuario.nome)
        usuario.email = dados.get("email", usuario.email)
        if dados.get("senha"):
            usuario.senha = dados["senha"]

        return self._repo.salvar(usuario)

    def deletar(self, id: int) -> None:
        usuario = self._repo.buscar_por_id(id)
        if not usuario:
            raise LookupError(f"Usuário {id} não encontrado.")
        self._repo.deletar(usuario)
