from flask import Blueprint, render_template, request, redirect

from services import usuario_service

usuario_bp = Blueprint("usuario", __name__)


@usuario_bp.route("/usuarios")
def listar():

    usuarios = usuario_service.listar()

    return render_template(
        "usuario/listar.html",
        usuarios=usuarios
    )


@usuario_bp.route("/usuarios/novo")
def novo():

    return render_template("usuario/cadastrar.html")


@usuario_bp.route("/usuarios/criar", methods=["POST"])
def criar():

    usuario_service.criar(
        request.form["nome"],
        request.form["email"],
        request.form["senha"],
        request.form["tipoPerfil"]
    )

    return redirect("/usuarios")


@usuario_bp.route("/usuarios/editar/<int:id>")
def editar(id):

    usuario = usuario_service.buscar(id)

    return render_template(
        "usuario/editar.html",
        usuario=usuario
    )


@usuario_bp.route("/usuarios/atualizar/<int:id>", methods=["POST"])
def atualizar(id):

    usuario_service.atualizar(
        id,
        request.form["nome"],
        request.form["email"],
        request.form["senha"],
        request.form["tipoPerfil"]
    )

    return redirect("/usuarios")


@usuario_bp.route("/usuarios/excluir/<int:id>")
def excluir(id):

    usuario_service.excluir(id)

    return redirect("/usuarios")