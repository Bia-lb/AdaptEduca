from flask import Blueprint, g, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from app.models.aluno import Aluno
from app.security import requer_auth
from app.services import adaptacao_engine as motor
from app.services import ia_adaptacao
from app.services.conteudo_service import ConteudoService

conteudo_bp = Blueprint("conteudo", __name__, url_prefix="/api")
_svc = ConteudoService()


def _erro(msg, status):
    return {"sucesso": False, "mensagem": msg}, status


@conteudo_bp.get("/conteudos/")
@requer_auth()
def listar():
    return {"sucesso": True, "dados": _svc.listar_para(g.usuario_id, g.perfil)}


@conteudo_bp.post("/conteudos/")
@requer_auth("Professor")
def criar():
    dados = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    try:
        conteudo = _svc.criar(dados, request.files.get("arquivo"), g.usuario_id)
    except PermissionError as exc:
        return _erro(str(exc), 403)
    except ValueError as exc:
        return _erro(str(exc), 422)
    return {"sucesso": True, "mensagem": "Conteúdo publicado.", "dados": conteudo.to_dict()}, 201


@conteudo_bp.get("/conteudos/<int:id>")
@requer_auth()
def buscar(id: int):
    c = _svc.buscar_visivel(id, g.usuario_id, g.perfil)
    if not c:
        return _erro("Conteúdo não encontrado.", 404)
    return {"sucesso": True, "dados": c.to_dict_completo()}


@conteudo_bp.get("/conteudos/<int:id>/arquivo")
@requer_auth()
def baixar(id: int):
    c = _svc.buscar_visivel(id, g.usuario_id, g.perfil)
    caminho = _svc.caminho_pdf(c) if c else None
    if not caminho:
        return _erro("Arquivo não encontrado.", 404)
    return send_file(caminho, mimetype="application/pdf", download_name=c.arquivoOriginal or "conteudo.pdf")


@conteudo_bp.delete("/conteudos/<int:id>")
@requer_auth("Professor")
def deletar(id: int):
    c = _svc.buscar_visivel(id, g.usuario_id, g.perfil)
    if not c or c.turma.professor_id != g.usuario_id:
        return _erro("Conteúdo não encontrado.", 404)
    _svc.deletar(c)
    return {"sucesso": True, "mensagem": "Conteúdo removido."}


@conteudo_bp.get("/conteudos/<int:id>/adaptacao")
@requer_auth()
def adaptacao(id: int):
    """?modo=resumo|simplificado|tdah|tea|mapa|audio|flashcards|para-mim"""
    c = _svc.buscar_visivel(id, g.usuario_id, g.perfil)
    if not c:
        return _erro("Conteúdo não encontrado.", 404)
    aluno = Aluno.buscar_por_id(g.usuario_id) if g.perfil == "Aluno" else None
    try:
        dados = _svc.adaptar(c, request.args.get("modo", "para-mim"), aluno, usuario_id=g.usuario_id)
    except ValueError as exc:
        return _erro(str(exc), 422)
    return {"sucesso": True, "dados": dados}


@conteudo_bp.post("/adaptar")
@requer_auth()
def adaptar_texto():
    """Adaptação avulsa de um texto colado pelo usuário (não é gravada)."""
    corpo = request.get_json(silent=True) or {}
    try:
        modo = corpo.get("modo", "")
        if modo not in motor.MODOS:
            raise ValueError(f"Modo inválido. Use: {', '.join(motor.MODOS)}.")
        resultado = ia_adaptacao.adaptar_com_fallback(g.usuario_id, modo, corpo.get("texto", ""))
    except ValueError as exc:
        return _erro(str(exc), 422)
    return {"sucesso": True, "dados": {"modo": corpo["modo"], "resultado": resultado}}


@conteudo_bp.errorhandler(RequestEntityTooLarge)
def _grande(_):
    return _erro("Arquivo muito grande (máximo de 10 MB).", 413)
