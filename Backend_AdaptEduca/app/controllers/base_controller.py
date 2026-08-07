from flask import jsonify, Response
from typing import Any


class BaseController:
    """
    Responsável apenas por serializar respostas HTTP.
    Decisões de negócio ficam nos Services.
    """

    @staticmethod
    def sucesso(dados: Any = None, mensagem: str = "OK", status: int = 200) -> Response:
        payload = {"sucesso": True, "mensagem": mensagem}
        if dados is not None:
            payload["dados"] = dados
        return jsonify(payload), status

    @staticmethod
    def erro(mensagem: str, status: int = 400) -> Response:
        return jsonify({"sucesso": False, "mensagem": mensagem}), status
