from flask import request
from app.services.responsavel_service import ResponsavelService
from .base_controller import BaseController


class ResponsavelController(BaseController):
    def __init__(self) -> None:
        self._service = ResponsavelService()

    def listar(self):
        responsaveis = self._service.listar()
        return self.sucesso([r.to_dict() for r in responsaveis])

    def buscar(self, id: int):
        responsavel = self._service.buscar(id)
        if not responsavel:
            return self.erro("Responsável não encontrado.", 404)
        return self.sucesso(responsavel.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        campos_obrigatorios = ["nome", "email", "senha"]
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            responsavel = self._service.criar(dados)
            return self.sucesso(responsavel.to_dict(), "Responsável criado.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        dados = request.get_json(silent=True) or {}
        try:
            responsavel = self._service.atualizar(id, dados)
            return self.sucesso(responsavel.to_dict(), "Responsável atualizado.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def deletar(self, id: int):
        try:
            self._service.deletar(id)
            return self.sucesso(mensagem="Responsável removido.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def dashboard(self, id: int):
        try:
            dados = self._service.dashboard(id)
            return self.sucesso(dados)
        except LookupError as exc:
            return self.erro(str(exc), 404)
