from flask import request
from app.services.turma_service import TurmaService
from .base_controller import BaseController


class TurmaController(BaseController):
    def __init__(self) -> None:
        self._service = TurmaService()

    def listar(self):
        turmas = self._service.listar()
        return self.sucesso([t.to_dict() for t in turmas])

    def buscar(self, id: int):
        turma = self._service.buscar(id)
        if not turma:
            return self.erro("Turma não encontrada.", 404)
        return self.sucesso(turma.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        campos_obrigatorios = ["codigo", "nome", "professor_id"]
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            turma = self._service.criar(dados)
            return self.sucesso(turma.to_dict(), "Turma criada.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        dados = request.get_json(silent=True) or {}
        try:
            turma = self._service.atualizar(id, dados)
            return self.sucesso(turma.to_dict(), "Turma atualizada.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def deletar(self, id: int):
        try:
            self._service.deletar(id)
            return self.sucesso(mensagem="Turma removida.")
        except LookupError as exc:
            return self.erro(str(exc), 404)
