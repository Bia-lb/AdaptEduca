from flask import Blueprint
from app.controllers.atividade_controller import AtividadeController
from app.security import requer_auth

atividade_bp = Blueprint("atividade", __name__, url_prefix="/api/atividades")
_ctrl = AtividadeController()


@atividade_bp.get("/")
@requer_auth()
def listar():
    return _ctrl.listar()


@atividade_bp.get("/<int:id>")
@requer_auth()
def buscar(id: int):
    return _ctrl.buscar(id)


@atividade_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@atividade_bp.put("/<int:id>")
@requer_auth("Professor")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@atividade_bp.delete("/<int:id>")
@requer_auth("Professor")
def deletar(id: int):
    return _ctrl.deletar(id)


@atividade_bp.put("/<int:id>/resposta")
@requer_auth("Aluno")
def salvar_resposta(id: int):
    return _ctrl.salvar_resposta(id)


@atividade_bp.get("/<int:id>/respostas")
@requer_auth("Professor")
def listar_respostas(id: int):
    return _ctrl.listar_respostas(id)
