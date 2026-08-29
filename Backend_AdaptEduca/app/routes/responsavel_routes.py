from flask import Blueprint, render_template
from app.controllers.responsavel_controller import ResponsavelController

responsavel_bp = Blueprint("responsavel", __name__, url_prefix="/responsavel")
_ctrl = ResponsavelController()

# ── Página HTML ──────────────────────────────────────────────────────────────

@responsavel_bp.get("/<int:id>/dashboard")
def dashboard_html(id: int):
    """Renderiza o dashboard do Responsável com dados reais."""
    return render_template("responsavel/dashboard.html", responsavel_id=id)


# ── API REST ─────────────────────────────────────────────────────────────────

@responsavel_bp.get("/api/")
def listar():
    return _ctrl.listar()


@responsavel_bp.get("/api/<int:id>")
def buscar(id: int):
    return _ctrl.buscar(id)


@responsavel_bp.post("/api/")
def criar():
    return _ctrl.criar()


@responsavel_bp.put("/api/<int:id>")
def atualizar(id: int):
    return _ctrl.atualizar(id)


@responsavel_bp.delete("/api/<int:id>")
def deletar(id: int):
    return _ctrl.deletar(id)


@responsavel_bp.get("/api/<int:id>/dashboard")
def dashboard_json(id: int):
    """Endpoint JSON que alimenta a página HTML via fetch."""
    return _ctrl.dashboard(id)
