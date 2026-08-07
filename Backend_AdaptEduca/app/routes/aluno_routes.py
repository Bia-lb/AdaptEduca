from flask import Blueprint
from app.controllers.aluno_controller import AlunoController

aluno_bp = Blueprint("aluno", __name__, url_prefix="/api/alunos")
_ctrl = AlunoController()


@aluno_bp.get("/")
def listar():
    return _ctrl.listar()


@aluno_bp.get("/<int:id>")
def buscar(id: int):
    return _ctrl.buscar(id)


@aluno_bp.post("/")
def criar():
    return _ctrl.criar()


@aluno_bp.put("/<int:id>")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@aluno_bp.delete("/<int:id>")
def deletar(id: int):
    return _ctrl.deletar(id)
