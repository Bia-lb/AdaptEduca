from flask import Blueprint
from app.controllers.aluno_controller import AlunoController
from app.security import requer_auth

aluno_bp = Blueprint("aluno", __name__, url_prefix="/api/alunos")
_ctrl = AlunoController()


# Rotas "me" vêm antes das rotas com <int:id>.
@aluno_bp.get("/me")
@requer_auth("Aluno")
def meu_perfil():
    return _ctrl.meu_perfil()


@aluno_bp.put("/me/questionario")
@requer_auth("Aluno")
def salvar_questionario():
    return _ctrl.salvar_questionario()


@aluno_bp.get("/")
@requer_auth("Professor")
def listar():
    return _ctrl.listar()


@aluno_bp.get("/<int:id>")
@requer_auth("Professor", proprio=True)
def buscar(id: int):
    return _ctrl.buscar(id)


@aluno_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@aluno_bp.put("/<int:id>")
@requer_auth(proprio=True)
def atualizar(id: int):
    return _ctrl.atualizar(id)


@aluno_bp.delete("/<int:id>")
@requer_auth(proprio=True)
def deletar(id: int):
    return _ctrl.deletar(id)
