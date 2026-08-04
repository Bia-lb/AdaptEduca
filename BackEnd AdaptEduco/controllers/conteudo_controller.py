from flask import Blueprint, render_template, request, redirect
from services import conteudo_service

conteudo_bp = Blueprint("conteudo", __name__)

@conteudo_bp.route("/conteudos")
def listar():
    conteudos = conteudo_service.listar()
    return render_template("conteudo/listar.html", conteudos=conteudos)

@conteudo_bp.route("/conteudos/novo")
def novo():
    return render_template("conteudo/cadastrar.html")

@conteudo_bp.route("/conteudos/criar", methods=["POST"])
def criar():
    conteudo_service.criar(
        request.form["turma_id"],
        request.form["titulo"],
        request.form["tipo"],
        request.form["arquivo"],
        request.form["dataPostagem"]
    )
    return redirect("/conteudos")

@conteudo_bp.route("/conteudos/editar/<int:id>")
def editar(id):
    conteudo = conteudo_service.buscar(id)
    return render_template("conteudo/editar.html", conteudo=conteudo)

@conteudo_bp.route("/conteudos/atualizar/<int:id>", methods=["POST"])
def atualizar(id):
    conteudo_service.atualizar(
        id,
        request.form["turma_id"],
        request.form["titulo"],
        request.form["tipo"],
        request.form["arquivo"],
        request.form["dataPostagem"]
    )
    return redirect("/conteudos")

@conteudo_bp.route("/conteudos/excluir/<int:id>")
def excluir(id):
    conteudo_service.excluir(id)
    return redirect("/conteudos")