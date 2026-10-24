import json

from flask import Blueprint, g, request

from app import db
from app.models.aluno import Aluno
from app.models.relatorio import Relatorio
from app.models.responsavel import Responsavel
from app.security import requer_auth
from app.services.progresso_service import ProgressoService
from app.services.responsavel_service import ResponsavelService

progresso_bp = Blueprint("progresso", __name__, url_prefix="/api")
_svc = ProgressoService()
_resp = ResponsavelService()


def _erro(msg, status):
    return {"sucesso": False, "mensagem": msg}, status


def _aluno_visivel(aluno_id: int):
    aluno = Aluno.buscar_por_id(aluno_id)
    if not aluno or not _svc.pode_ver_aluno(g.usuario_id, g.perfil, aluno):
        return None
    return aluno


# ── RF16 / RF17 / RF19 ───────────────────────────────────────────────────────
@progresso_bp.get("/progresso/aluno/<int:id>")
@requer_auth()
def progresso_aluno(id: int):
    aluno = _aluno_visivel(id)
    if not aluno:
        return _erro("Aluno não encontrado.", 404)
    return {"sucesso": True, "dados": _svc.relatorio_aluno(aluno, request.args.get("dias", 30, type=int))}


@progresso_bp.get("/progresso/professor")
@requer_auth("Professor")
def progresso_professor():
    return {"sucesso": True, "dados": _svc.dashboard_professor(g.usuario_id, request.args.get("dias", 30, type=int))}


@progresso_bp.get("/progresso/responsavel")
@requer_auth("Responsavel")
def progresso_responsavel():
    return {"sucesso": True, "dados": _svc.painel_responsavel(Responsavel.buscar_por_id(g.usuario_id))}


# ── vínculo responsável ↔ filho ──────────────────────────────────────────────
@progresso_bp.post("/responsaveis/me/filhos")
@requer_auth("Responsavel")
def vincular():
    corpo = request.get_json(silent=True) or {}
    try:
        aluno = _resp.vincular_filho(g.usuario_id, corpo.get("matricula"), corpo.get("email"))
    except LookupError as exc:
        return _erro(str(exc), 404)
    except ValueError as exc:
        return _erro(str(exc), 409)
    return {"sucesso": True, "mensagem": "Aluno vinculado.", "dados": {"id": aluno.id, "nome": aluno.nome}}, 201


@progresso_bp.delete("/responsaveis/me/filhos/<int:aluno_id>")
@requer_auth("Responsavel")
def desvincular(aluno_id: int):
    try:
        _resp.desvincular_filho(g.usuario_id, aluno_id)
    except LookupError as exc:
        return _erro(str(exc), 404)
    return {"sucesso": True, "mensagem": "Vínculo removido."}


# ── RF20: relatórios de evolução ─────────────────────────────────────────────
@progresso_bp.post("/relatorios/aluno/<int:id>")
@requer_auth("Professor", "Responsavel", "Aluno")
def gerar_relatorio(id: int):
    aluno = _aluno_visivel(id)
    if not aluno:
        return _erro("Aluno não encontrado.", 404)
    dias = (request.get_json(silent=True) or {}).get("dias", 30)
    try:
        rel = _svc.salvar_relatorio(aluno, int(dias))
    except (TypeError, ValueError):
        return _erro("Período inválido.", 422)
    return {"sucesso": True, "mensagem": "Relatório gerado.", "dados": {**rel.to_dict(), "relatorio": json.loads(rel.dados)}}, 201


@progresso_bp.get("/relatorios/aluno/<int:id>")
@requer_auth()
def listar_relatorios(id: int):
    aluno = _aluno_visivel(id)
    if not aluno:
        return _erro("Aluno não encontrado.", 404)
    itens = Relatorio.query.filter_by(aluno_id=id).order_by(Relatorio.id.desc()).all()
    return {"sucesso": True, "dados": [r.to_dict() for r in itens]}


@progresso_bp.get("/relatorios/<int:id>")
@requer_auth()
def buscar_relatorio(id: int):
    rel = db.session.get(Relatorio, id)
    aluno = _aluno_visivel(rel.aluno_id) if rel else None
    if not aluno:
        return _erro("Relatório não encontrado.", 404)
    return {"sucesso": True, "dados": {**rel.to_dict(), "relatorio": json.loads(rel.dados or "{}")}}
