from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError


def criar_blueprint(recurso, service):
    blueprint = Blueprint(recurso, __name__, url_prefix=f"/api/{recurso}")

    @blueprint.get("")
    def listar():
        return jsonify([registro.to_dict() for registro in service.listar()])

    @blueprint.get("/<int:identificador>")
    def buscar(identificador):
        try:
            return jsonify(service.buscar(identificador).to_dict())
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @blueprint.post("")
    def criar():
        try:
            registro = service.criar(request.get_json(silent=True) or {})
            return jsonify(registro.to_dict()), 201
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except IntegrityError:
            return jsonify({"erro": "Os dados informados violam uma restrição do banco."}), 409

    @blueprint.put("/<int:identificador>")
    def atualizar(identificador):
        try:
            registro = service.atualizar(identificador, request.get_json(silent=True) or {})
            return jsonify(registro.to_dict())
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except IntegrityError:
            return jsonify({"erro": "Os dados informados violam uma restrição do banco."}), 409

    @blueprint.delete("/<int:identificador>")
    def excluir(identificador):
        try:
            service.excluir(identificador)
            return "", 204
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        except IntegrityError:
            return jsonify({"erro": "O registro possui vínculos e não pode ser excluído."}), 409

    return blueprint
