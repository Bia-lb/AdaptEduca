from flask import request
from app.services.usuario_service import UsuarioService
from .base_controller import BaseController


class UsuarioController(BaseController):
    def __init__(self) -> None:
        self._service = UsuarioService()

    def listar(self):
        usuarios = self._service.listar()
        return self.sucesso([u.to_dict() for u in usuarios])

    def buscar(self, id: int):
        usuario = self._service.buscar(id)
        if not usuario:
            return self.erro("Usuário não encontrado.", 404)
        return self.sucesso(usuario.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        campos_obrigatorios = ["nome", "email", "senha", "tipoPerfil"]
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            usuario = self._service.criar(dados)
            return self.sucesso(usuario.to_dict(), "Usuário criado.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        dados = request.get_json(silent=True) or {}
        try:
            usuario = self._service.atualizar(id, dados)
            return self.sucesso(usuario.to_dict(), "Usuário atualizado.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def deletar(self, id: int):
        try:
            self._service.deletar(id)
            return self.sucesso(mensagem="Usuário removido.")
        except LookupError as exc:
            return self.erro(str(exc), 404)
