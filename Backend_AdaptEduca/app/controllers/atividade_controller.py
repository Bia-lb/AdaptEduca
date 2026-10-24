from flask import g, request
from app.services.atividade_service import AtividadeService
from app.services.turma_service import TurmaService
from .base_controller import BaseController


class AtividadeController(BaseController):
    def __init__(self) -> None:
        self._service = AtividadeService()
        self._turmas = TurmaService()

    def _visivel(self, id: int):
        atividade = self._service.buscar(id)
        if not atividade or not self._turmas.tem_acesso(atividade.turma, g.usuario_id, g.perfil):
            return None
        return atividade

    def _do_professor(self, id: int):
        atividade = self._service.buscar(id)
        if not atividade:
            return None, self.erro("Atividade não encontrada.", 404)
        if atividade.turma.professor_id != g.usuario_id:
            return None, self.erro("Acesso negado.", 403)
        return atividade, None

    def listar(self):
        return self.sucesso(self._service.listar_para(g.usuario_id, g.perfil))

    def buscar(self, id: int):
        atividade = self._visivel(id)
        if not atividade:
            return self.erro("Atividade não encontrada.", 404)
        dados = atividade.to_dict()
        if g.perfil == "Aluno":
            resposta = self._service.resposta_do_aluno(id, g.usuario_id)
            dados["minhaResposta"] = resposta.to_dict() if resposta else None
        return self.sucesso(dados)

    def criar(self):
        dados = request.get_json(silent=True) or {}
        for campo in ["titulo", "turma_id"]:
            if not dados.get(campo):
                return self.erro(f"Campo obrigatório ausente: {campo}.", 422)
        try:
            atividade = self._service.criar(dados, g.usuario_id)
            return self.sucesso(atividade.to_dict(), "Atividade criada.", 201)
        except PermissionError as exc:
            return self.erro(str(exc), 403)
        except ValueError as exc:
            return self.erro(str(exc), 422)

    def atualizar(self, id: int):
        _, erro = self._do_professor(id)
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        try:
            atividade = self._service.atualizar(id, dados)
        except ValueError as exc:
            return self.erro(str(exc), 422)
        return self.sucesso(atividade.to_dict(), "Atividade atualizada.")

    def deletar(self, id: int):
        _, erro = self._do_professor(id)
        if erro:
            return erro
        self._service.deletar(id)
        return self.sucesso(mensagem="Atividade removida.")

    # ── respostas ───────────────────────────────────────────────────────────
    def salvar_resposta(self, id: int):
        atividade = self._visivel(id)
        if not atividade:
            return self.erro("Atividade não encontrada.", 404)
        dados = request.get_json(silent=True) or {}
        try:
            resposta = self._service.salvar_resposta(
                atividade, g.usuario_id, dados.get("respostas"), bool(dados.get("enviar")),
                dados.get("etapasConcluidas"))
        except PermissionError as exc:
            return self.erro(str(exc), 403)
        except ValueError as exc:
            return self.erro(str(exc), 422)
        msg = "Atividade enviada." if resposta.status == "Enviada" else "Rascunho salvo."
        return self.sucesso(resposta.to_dict(), msg)

    def listar_respostas(self, id: int):
        atividade, erro = self._do_professor(id)
        if erro:
            return erro
        return self.sucesso(self._service.listar_respostas(atividade))
