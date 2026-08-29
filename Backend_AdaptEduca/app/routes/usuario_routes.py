from flask import Blueprint
from app.controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint("usuario", __name__, url_prefix="/api/usuarios")
_ctrl = UsuarioController()


@usuario_bp.get("/")
def listar():
    return _ctrl.listar()


@usuario_bp.get("/<int:id>")
def buscar(id: int):
    return _ctrl.buscar(id)


@usuario_bp.post("/")
def criar():
    return _ctrl.criar()


@usuario_bp.put("/<int:id>")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@usuario_bp.delete("/<int:id>")
def deletar(id: int):
    return _ctrl.deletar(id)
