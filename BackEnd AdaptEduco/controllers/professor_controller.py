from flask import Blueprint, render_template, request, redirect
from services import professor_service

professor_bp = Blueprint("professor", __name__)

@professor_bp.route("/professores")
def listar():
    professores = professor_service.listar()
    return render_template("professor/listar.html", professores=professores)

@professor_bp.route("/professores/novo")
def novo():
    return render_template("professor/cadastrar.html")

@professor_bp.route("/professores/criar", methods=["POST"])
def criar():
    professor_service.criar(
        request.form["usuario_id"],
        request.form["formacao"],
        request.form["disciplina"]
    )
    return redirect("/professores")

@professor_bp.route("/professores/editar/<int:id>")
def editar(id):
    professor = professor_service.buscar(id)
    return render_template("professor/editar.html", professor=professor)

@professor_bp.route("/professores/atualizar/<int:id>", methods=["POST"])
def atualizar(id):
    professor_service.atualizar(
        id,
        request.form["usuario_id"],
        request.form["formacao"],
        request.form["disciplina"]
    )
    return redirect("/professores")

@professor_bp.route("/professores/excluir/<int:id>")
def excluir(id):
    professor_service.excluir(id)
    return redirect("/professores") 