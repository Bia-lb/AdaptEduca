from flask import request
from app.services.aluno_service import AlunoService
from .base_controller import BaseController


class AlunoController(BaseController):
    def __init__(self) -> None:
        self._service = AlunoService()

    def listar(self):
        alunos = self._service.listar()
        return self.sucesso([a.to_dict() for a in alunos])

    def buscar(self, id: int):
        aluno = self._service.buscar(id)
        if not aluno:
            return self.erro("Aluno não encontrado.", 404)
        return self.sucesso(aluno.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        campos_obrigatorios = ["nome", "email", "senha", "matricula"]
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            aluno = self._service.criar(dados)
            return self.sucesso(aluno.to_dict(), "Aluno criado.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        dados = request.get_json(silent=True) or {}
        try:
            aluno = self._service.atualizar(id, dados)
            return self.sucesso(aluno.to_dict(), "Aluno atualizado.")
        except LookupError as exc:
            return self.erro(str(exc), 404)

    def deletar(self, id: int):
        try:
            self._service.deletar(id)
            return self.sucesso(mensagem="Aluno removido.")
        except LookupError as exc:
            return self.erro(str(exc), 404)
