from flask import Blueprint
from app.controllers.turma_controller import TurmaController
from app.security import requer_auth

turma_bp = Blueprint("turma", __name__, url_prefix="/api/turmas")
_ctrl = TurmaController()


@turma_bp.get("/")
@requer_auth()
def listar():
    return _ctrl.listar()


@turma_bp.get("/<int:id>")
@requer_auth()
def buscar(id: int):
    return _ctrl.buscar(id)


@turma_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@turma_bp.put("/<int:id>")
@requer_auth("Professor")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@turma_bp.delete("/<int:id>")
@requer_auth("Professor")
def deletar(id: int):
    return _ctrl.deletar(id)


@turma_bp.get("/<int:id>/alunos")
@requer_auth("Professor")
def listar_alunos(id: int):
    return _ctrl.listar_alunos(id)


@turma_bp.post("/<int:id>/alunos")
@requer_auth("Professor")
def adicionar_aluno(id: int):
    return _ctrl.adicionar_aluno(id)


@turma_bp.delete("/<int:id>/alunos/<int:aluno_id>")
@requer_auth("Professor")
def remover_aluno(id: int, aluno_id: int):
    return _ctrl.remover_aluno(id, aluno_id)
