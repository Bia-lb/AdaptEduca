from flask import request
from app.services.atividade_service import AtividadeService
from .base_controller import BaseController


class AtividadeController(BaseController):
    def __init__(self) -> None:
        self._service = AtividadeService()

    def listar(self):
        atividades = self._service.listar()
        return self.sucesso([a.to_dict() for a in atividades])

    def buscar(self, id: int):
        atividade = self._service.buscar(id)
        if not atividade:
            return self.erro("Atividade não encontrada.", 404)
        return self.sucesso(atividade.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        campos_obrigatorios = ["titulo", "turma_id"]
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            atividade = self._service.criar(dados)
            return self.sucesso(atividade.to_dict(), "Atividade criada.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        dados = request.get_json(silent=True) or {}
        try:
            atividade = self._service.atualizar(id, dados)
            return self.sucesso(atividade.to_dict(), "Atividade atualizada.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def deletar(self, id: int):
        try:
            self._service.deletar(id)
            return self.sucesso(mensagem="Atividade removida.")
        except LookupError as exc:
            return self.erro(str(exc), 404)
