from flask import Blueprint, g, request

from app.models.aluno import Aluno
from app.security import requer_auth
from app.services import ia_acompanhamento, ia_service as ia, ia_tutor
from app.services.conteudo_service import ConteudoService
from app.services.progresso_service import ProgressoService
from flask import current_app

ia_bp = Blueprint("ia", __name__, url_prefix="/api")
_conteudos = ConteudoService()
_progresso = ProgressoService()


def _erro(msg, status):
    return {"sucesso": False, "mensagem": msg}, status


def _tratar(exc):
    if isinstance(exc, ia.IACotaExcedida):
        return _erro(str(exc), 429)
    if isinstance(exc, ia.IAIndisponivel):
        return _erro("O assistente de IA não está disponível no momento.", 503)
    return _erro("O assistente de IA não conseguiu responder agora. Tente novamente em instantes.", 502)


@ia_bp.get("/ia/status")
@requer_auth()
def status():
    return {"sucesso": True, "dados": {"disponivel": ia.disponivel(), "restante": ia.restante(g.usuario_id),
                                       "limiteDiario": current_app.config["IA_LIMITE_DIARIO"]}}


@ia_bp.post("/tutor/mensagem")
@requer_auth("Aluno", "Professor")
def tutor():
    corpo = request.get_json(silent=True) or {}
    texto, quest = "", {}
    if corpo.get("conteudo_id") is not None:
        try:
            conteudo = _conteudos.buscar_visivel(int(corpo["conteudo_id"]), g.usuario_id, g.perfil)
        except (TypeError, ValueError):
            conteudo = None
        if not conteudo:
            return _erro("Conteúdo não encontrado.", 404)
        texto = conteudo.texto or ""
    elif isinstance(corpo.get("texto"), str):
        texto = corpo["texto"]
    if g.perfil == "Aluno":
        aluno = Aluno.buscar_por_id(g.usuario_id)
        quest = aluno.respostas_questionario() if aluno else {}
    try:
        resposta = ia_tutor.responder(g.usuario_id, corpo.get("mensagens"), texto, quest)
    except ValueError as exc:
        return _erro(str(exc), 422)
    except (ia.IAIndisponivel, ia.IACotaExcedida, ia.IAFalha) as exc:
        return _tratar(exc)
    return {"sucesso": True, "dados": {"resposta": resposta, "restante": ia.restante(g.usuario_id)}}


@ia_bp.post("/progresso/aluno/<int:id>/analise")
@requer_auth()
def analise(id: int):
    aluno = Aluno.buscar_por_id(id)
    if not aluno or not _progresso.pode_ver_aluno(g.usuario_id, g.perfil, aluno):
        return _erro("Aluno não encontrado.", 404)
    dias = (request.get_json(silent=True) or {}).get("dias", 30)
    try:
        dias = max(7, min(int(dias), 365))
    except (TypeError, ValueError):
        dias = 30
    try:
        dados = ia_acompanhamento.analisar(g.usuario_id, g.perfil, aluno, _progresso, dias)
    except (ia.IAIndisponivel, ia.IACotaExcedida, ia.IAFalha) as exc:
        return _tratar(exc)
    return {"sucesso": True, "dados": dados}
