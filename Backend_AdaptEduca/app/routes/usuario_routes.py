from flask import Blueprint
from app.controllers.usuario_controller import UsuarioController
from app.security import requer_auth

usuario_bp = Blueprint("usuario", __name__, url_prefix="/api/usuarios")
_ctrl = UsuarioController()


@usuario_bp.get("/")
@requer_auth("Professor")
def listar():
    return _ctrl.listar()


@usuario_bp.get("/<int:id>")
@requer_auth("Professor", proprio=True)
def buscar(id: int):
    return _ctrl.buscar(id)


@usuario_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@usuario_bp.put("/<int:id>")
@requer_auth(proprio=True)
def atualizar(id: int):
    return _ctrl.atualizar(id)


@usuario_bp.delete("/<int:id>")
@requer_auth(proprio=True)
def deletar(id: int):
    return _ctrl.deletar(id)
