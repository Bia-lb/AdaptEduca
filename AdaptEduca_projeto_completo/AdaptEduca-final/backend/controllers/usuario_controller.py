from flask import Blueprint, jsonify, request
from controllers.crud_controller import criar_blueprint
from services.usuario_service import usuario_service

usuario_bp = criar_blueprint("usuarios", usuario_service)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    try:
        usuario = usuario_service.autenticar(dados.get("email", ""), dados.get("senha", ""))
        return jsonify(usuario.to_dict())
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 401
