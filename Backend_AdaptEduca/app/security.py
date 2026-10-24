"""Autenticação por token assinado e controle de acesso por perfil."""
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="adapteduca-auth")


def gerar_token(usuario) -> str:
    return _serializer().dumps({"id": usuario.id, "perfil": usuario.tipoPerfil})


def _ler_token():
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Bearer "):
        return None
    try:
        return _serializer().loads(
            cabecalho[7:], max_age=current_app.config.get("TOKEN_MAX_AGE", 43200)
        )
    except (BadSignature, SignatureExpired):
        return None


def _negado(mensagem, status):
    return {"sucesso": False, "mensagem": mensagem}, status


def requer_auth(*perfis, proprio=False):
    """Exige token válido. `perfis` restringe por tipoPerfil; com `proprio=True`
    o usuário também passa se `id` da URL for o dele."""

    def decorador(funcao):
        @wraps(funcao)
        def interno(*args, **kwargs):
            dados = _ler_token()
            if not dados:
                return _negado("Autenticação necessária.", 401)
            g.usuario_id = dados["id"]
            g.perfil = dados["perfil"]
            if perfis or proprio:
                eh_proprio = proprio and kwargs.get("id") == g.usuario_id
                if g.perfil not in perfis and not eh_proprio:
                    return _negado("Acesso negado.", 403)
            return funcao(*args, **kwargs)

        return interno

    return decorador
