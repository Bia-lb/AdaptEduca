from flask import Blueprint
from app.controllers.atividade_controller import AtividadeController
from app.security import requer_auth
import os
from flask import g, current_app, send_file
from app.services.atividade_service import AtividadeService
from app.services.turma_service import TurmaService


atividade_bp = Blueprint("atividade", __name__, url_prefix="/api/atividades")
_ctrl = AtividadeController()


@atividade_bp.get("/")
@requer_auth()
def listar():
    return _ctrl.listar()


@atividade_bp.get("/<int:id>")
@requer_auth()
def buscar(id: int):
    return _ctrl.buscar(id)


@atividade_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@atividade_bp.put("/<int:id>")
@requer_auth("Professor")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@atividade_bp.delete("/<int:id>")
@requer_auth("Professor")
def deletar(id: int):
    return _ctrl.deletar(id)


@atividade_bp.put("/<int:id>/resposta")
@requer_auth("Aluno")
def salvar_resposta(id: int):
    return _ctrl.salvar_resposta(id)


@atividade_bp.get("/<int:id>/respostas")
@requer_auth("Professor")
def listar_respostas(id: int):
    return _ctrl.listar_respostas(id)


@atividade_bp.get("/<int:id>/pdf")
@requer_auth()
def baixar_pdf(id: int):
    atividade = AtividadeService().buscar(id)

    if not atividade:
        return {
            "sucesso": False,
            "mensagem": "Atividade não encontrada."
        }, 404

    if not TurmaService().tem_acesso(
        atividade.turma, g.usuario_id, g.perfil
    ):
        return {
            "sucesso": False,
            "mensagem": "Acesso negado."
        }, 403

    if not atividade.pdfArquivo:
        return {
            "sucesso": False,
            "mensagem": "Esta atividade não possui PDF."
        }, 404

    pasta = os.path.join(
        current_app.config["UPLOAD_DIR"],
        "atividades"
    )

    caminho = os.path.join(
        pasta,
        os.path.basename(atividade.pdfArquivo)
    )

    if not os.path.isfile(caminho):
        return {
            "sucesso": False,
            "mensagem": "Arquivo não encontrado."
        }, 404

    return send_file(
        caminho,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=atividade.pdfOriginal or "atividade.pdf"
    )
