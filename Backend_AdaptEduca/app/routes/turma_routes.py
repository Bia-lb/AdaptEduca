from flask import Blueprint
from app.controllers.turma_controller import TurmaController

turma_bp = Blueprint("turma", __name__, url_prefix="/api/turmas")
_ctrl = TurmaController()


@turma_bp.get("/")
def listar():
    return _ctrl.listar()


@turma_bp.get("/<int:id>")
def buscar(id: int):
    return _ctrl.buscar(id)


@turma_bp.post("/")
def criar():
    return _ctrl.criar()


@turma_bp.put("/<int:id>")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@turma_bp.delete("/<int:id>")
def deletar(id: int):
    return _ctrl.deletar(id)
