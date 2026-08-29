from flask import Blueprint, request
from app.services.usuario_service import UsuarioService
from app.services.aluno_service import AlunoService
from app.services.responsavel_service import ResponsavelService
from app.models.professor import Professor
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""
    if not email or not senha:
        return {"sucesso": False, "mensagem": "E-mail e senha são obrigatórios."}, 422

    usuarios = Usuario.listar()
    usuario = next((u for u in usuarios if u.email.lower() == email.lower()), None)
    if not usuario or usuario.senha != senha:
        return {"sucesso": False, "mensagem": "E-mail ou senha incorretos."}, 401

    return {"sucesso": True, "dados": usuario.to_dict()}


@auth_bp.post("/register")
def register():
    dados = request.get_json(silent=True) or {}
    role = dados.get("tipoPerfil")
    required = ["nome", "email", "senha", "tipoPerfil"]
    missing = next((campo for campo in required if not dados.get(campo)), None)
    if missing:
        return {"sucesso": False, "mensagem": f"Campo obrigatório ausente: {missing}."}, 422

    try:
        if role == "Aluno":
            aluno_dados = dict(dados)
            aluno_dados.setdefault("matricula", dados.get("matricula") or f"WEB{__import__('time').time_ns()}")
            usuario = AlunoService().criar(aluno_dados)
        elif role == "Responsavel":
            usuario = ResponsavelService().criar(dados)
        elif role == "Professor":
            if not UsuarioService().email_disponivel(dados["email"]):
                raise ValueError(f"E-mail {dados['email']!r} já cadastrado.")
            usuario = Professor.criar(
                nome=dados["nome"], email=dados["email"], senha=dados["senha"],
                tipoPerfil="Professor", formacao=dados.get("formacao"),
                disciplina=dados.get("disciplina"),
            )
        else:
            return {"sucesso": False, "mensagem": "Perfil inválido."}, 422
        return {"sucesso": True, "mensagem": "Conta criada.", "dados": usuario.to_dict()}, 201
    except ValueError as exc:
        return {"sucesso": False, "mensagem": str(exc)}, 409
