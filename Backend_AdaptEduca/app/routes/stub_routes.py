"""
Rotas stub para entidades ainda sem CRUD completo.
Retornam 501 Not Implemented para sinalizar que o endpoint existe
mas ainda não foi implementado.
"""
from flask import Blueprint, jsonify
from app.security import requer_auth

stub_bp = Blueprint("stub", __name__)

_STUBS = [
    ("/api/professores", "Professor"),
    ("/api/adaptacoes", "Adaptacao"),
]


def _stub_handler(entidade: str):
    def handler(*args, **kwargs):
        return jsonify({
            "sucesso": False,
            "mensagem": f"CRUD de {entidade} ainda não implementado (stub).",
        }), 501
    return handler


for _prefixo, _entidade in _STUBS:
    for _metodo in ["GET", "POST"]:
        stub_bp.add_url_rule(
            f"{_prefixo}/",
            endpoint=f"stub_{_entidade}_{_metodo}",
            view_func=requer_auth()(_stub_handler(_entidade)),
            methods=[_metodo],
        )
    stub_bp.add_url_rule(
        f"{_prefixo}/<int:id>",
        endpoint=f"stub_{_entidade}_item",
        view_func=requer_auth()(_stub_handler(_entidade)),
        methods=["GET", "PUT", "DELETE"],
    )
