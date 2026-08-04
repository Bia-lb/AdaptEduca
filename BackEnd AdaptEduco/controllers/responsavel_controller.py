from flask import Blueprint, render_template, request, redirect
from services import responsavel_service

responsavel_bp = Blueprint("responsavel", __name__)

@responsavel_bp.route("/responsaveis")
def listar():
    responsaveis = responsavel_service.listar()
    return render_template("responsavel/listar.html", responsaveis=responsaveis)

@responsavel_bp.route("/responsaveis/novo")
def novo():
    return render_template("responsavel/cadastrar.html")

@responsavel_bp.route("/responsaveis/criar", methods=["POST"])
def criar():
    responsavel_service.criar(
        request.form["usuario_id"],
        request.form["parentesco"],
        request.form["telefone"]
    )
    return redirect("/responsaveis")

@responsavel_bp.route("/responsaveis/editar/<int:id>")
def editar(id):
    responsavel = responsavel_service.buscar(id)
    return render_template("responsavel/editar.html", responsavel=responsavel)

@responsavel_bp.route("/responsaveis/atualizar/<int:id>", methods=["POST"])
def atualizar(id):
    responsavel_service.atualizar(
        id,
        request.form["usuario_id"],
        request.form["parentesco"],
        request.form["telefone"]
    )
    return redirect("/responsaveis")

@responsavel_bp.route("/responsaveis/excluir/<int:id>")
def excluir(id):
    responsavel_service.excluir(id)
    return redirect("/responsaveis")