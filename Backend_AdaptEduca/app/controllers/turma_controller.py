from flask import g, request
from app.services.turma_service import TurmaService
from .base_controller import BaseController


class TurmaController(BaseController):
    def __init__(self) -> None:
        self._service = TurmaService()

    def _turma_do_professor(self, id: int):
        """Retorna (turma, erro). Só o professor dono pode alterar a turma."""
        turma = self._service.buscar(id)
        if not turma:
            return None, self.erro("Turma não encontrada.", 404)
        if turma.professor_id != g.usuario_id:
            return None, self.erro("Acesso negado.", 403)
        return turma, None

    def listar(self):
        turmas = self._service.listar_para(g.usuario_id, g.perfil)
        return self.sucesso([t.to_dict() for t in turmas])

    def buscar(self, id: int):
        turma = self._service.buscar(id)
        if not turma or not self._service.tem_acesso(turma, g.usuario_id, g.perfil):
            return self.erro("Turma não encontrada.", 404)
        return self.sucesso(turma.to_dict())

    def criar(self):
        dados = request.get_json(silent=True) or {}
        for campo in ["codigo", "nome"]:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            turma = self._service.criar(dados, g.usuario_id)
            return self.sucesso(turma.to_dict(), "Turma criada.", 201)
        except ValueError as exc:
            return self.erro(str(exc), 409)

    def atualizar(self, id: int):
        turma, erro = self._turma_do_professor(id)
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        turma = self._service.atualizar(id, dados)
        return self.sucesso(turma.to_dict(), "Turma atualizada.")

    def deletar(self, id: int):
        turma, erro = self._turma_do_professor(id)
        if erro:
            return erro
        self._service.deletar(id)
        return self.sucesso(mensagem="Turma removida.")

    # ── alunos da turma ─────────────────────────────────────────────────────
    def listar_alunos(self, id: int):
        turma = self._service.buscar(id)
        if not turma or not self._service.tem_acesso(turma, g.usuario_id, g.perfil):
            return self.erro("Turma não encontrada.", 404)
        if g.perfil != "Professor":
            return self.erro("Acesso negado.", 403)
        alunos = sorted(turma.alunos, key=lambda a: a.nome)
        return self.sucesso([
            {"id": a.id, "nome": a.nome, "email": a.email,
             "matricula": a.matricula, "progresso": a.progresso}
            for a in alunos
        ])

    def adicionar_aluno(self, id: int):
        turma, erro = self._turma_do_professor(id)
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        try:
            aluno = self._service.adicionar_aluno(turma, dados)
        except LookupError as exc:
            return self.erro(str(exc), 404)
        except ValueError as exc:
            return self.erro(str(exc), 409)
        return self.sucesso({"id": aluno.id, "nome": aluno.nome}, "Aluno adicionado à turma.", 201)

    def remover_aluno(self, id: int, aluno_id: int):
        turma, erro = self._turma_do_professor(id)
        if erro:
            return erro
        try:
            self._service.remover_aluno(turma, aluno_id)
        except LookupError as exc:
            return self.erro(str(exc), 404)
        return self.sucesso(mensagem="Aluno removido da turma.")
