from flask import Blueprint, g, request

from app.security import requer_auth
from app.services.feedback_service import FeedbackService

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedbacks")
_svc = FeedbackService()


def _erro(msg, status):
    return {"sucesso": False, "mensagem": msg}, status


@feedback_bp.get("/")
@requer_auth()
def listar():
    itens = _svc.listar_para(g.usuario_id, g.perfil,
                             request.args.get("atividade_id", type=int),
                             request.args.get("aluno_id", type=int))
    return {"sucesso": True, "dados": [_svc.dict_com_autor(f) for f in itens]}


@feedback_bp.post("/")
@requer_auth("Professor")
def criar():
    try:
        fb = _svc.criar(request.get_json(silent=True) or {}, g.usuario_id)
    except PermissionError as exc:
        return _erro(str(exc), 403)
    except LookupError as exc:
        return _erro(str(exc), 404)
    except ValueError as exc:
        return _erro(str(exc), 422)
    return {"sucesso": True, "mensagem": "Feedback enviado.", "dados": _svc.dict_com_autor(fb)}, 201


@feedback_bp.delete("/<int:id>")
@requer_auth("Professor")
def deletar(id: int):
    try:
        _svc.deletar(id, g.usuario_id)
    except LookupError as exc:
        return _erro(str(exc), 404)
    return {"sucesso": True, "mensagem": "Feedback removido."}
