"""
Rotas stub para entidades ainda sem CRUD completo.
Retornam 501 Not Implemented para sinalizar que o endpoint existe
mas ainda não foi implementado.
"""
from flask import Blueprint, jsonify

stub_bp = Blueprint("stub", __name__)

_STUBS = [
    ("/api/professores", "Professor"),
    ("/api/conteudos", "Conteudo"),
    ("/api/adaptacoes", "Adaptacao"),
    ("/api/feedbacks", "Feedback"),
    ("/api/relatorios", "Relatorio"),
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
            view_func=_stub_handler(_entidade),
            methods=[_metodo],
        )
    stub_bp.add_url_rule(
        f"{_prefixo}/<int:id>",
        endpoint=f"stub_{_entidade}_item",
        view_func=_stub_handler(_entidade),
        methods=["GET", "PUT", "DELETE"],
    )
