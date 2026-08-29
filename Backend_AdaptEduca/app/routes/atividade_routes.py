from flask import Blueprint
from app.controllers.atividade_controller import AtividadeController

atividade_bp = Blueprint("atividade", __name__, url_prefix="/api/atividades")
_ctrl = AtividadeController()


@atividade_bp.get("/")
def listar():
    return _ctrl.listar()


@atividade_bp.get("/<int:id>")
def buscar(id: int):
    return _ctrl.buscar(id)


@atividade_bp.post("/")
def criar():
    return _ctrl.criar()


@atividade_bp.put("/<int:id>")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@atividade_bp.delete("/<int:id>")
def deletar(id: int):
    return _ctrl.deletar(id)
