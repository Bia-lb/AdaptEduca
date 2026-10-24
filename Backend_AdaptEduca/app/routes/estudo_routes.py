from flask import Blueprint, g, request

from app.models.aluno import Aluno
from app.security import requer_auth
from app.services.estudo_service import EstudoService

estudo_bp = Blueprint("estudo", __name__, url_prefix="/api/estudo")
_svc = EstudoService()


@estudo_bp.get("/modos")
@requer_auth("Aluno")
def modos():
    return {"sucesso": True, "dados": _svc.modos(Aluno.buscar_por_id(g.usuario_id))}


@estudo_bp.post("/sessoes")
@requer_auth("Aluno")
def registrar():
    corpo = request.get_json(silent=True) or {}
    try:
        sessao = _svc.registrar(Aluno.buscar_por_id(g.usuario_id), corpo.get("modo"),
                                corpo.get("segundos"), corpo.get("conteudo_id"))
    except PermissionError as exc:
        return {"sucesso": False, "mensagem": str(exc)}, 404
    except ValueError as exc:
        return {"sucesso": False, "mensagem": str(exc)}, 422
    return {"sucesso": True, "mensagem": "Sessão registrada.", "dados": sessao.to_dict()}, 201


@estudo_bp.get("/sessoes")
@requer_auth("Aluno")
def listar_sessoes():
    from app.models.conteudo import Conteudo
    from app.models.sessao_estudo import SessaoEstudo
    itens = (SessaoEstudo.query.filter_by(aluno_id=g.usuario_id)
             .order_by(SessaoEstudo.iniciadaEm.desc()).limit(30).all())
    saida = []
    for s in itens:
        d = s.to_dict()
        c = Conteudo.query.get(s.conteudo_id) if s.conteudo_id else None
        d["conteudoTitulo"] = c.titulo if c else None
        saida.append(d)
    return {"sucesso": True, "dados": saida}
