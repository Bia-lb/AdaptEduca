import hashlib

from flask import Blueprint, current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func

from app import db
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.security import gerar_token, requer_auth
from app.services.aluno_service import AlunoService
from app.services.responsavel_service import ResponsavelService
from app.services import email_service
from app.services.usuario_service import UsuarioService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MIN_SENHA = 8


def _perfil_completo(usuario: Usuario) -> dict:
    """Dados do usuário conforme o perfil (alunos incluem o estado do questionário)."""
    if usuario.tipoPerfil == "Aluno":
        aluno = Aluno.buscar_por_id(usuario.id)
        if aluno:
            return aluno.to_dict()
    return usuario.to_dict()


def _resposta_auth(usuario: Usuario, status: int = 200, mensagem: str = "OK"):
    return {
        "sucesso": True, "mensagem": mensagem,
        "dados": _perfil_completo(usuario), "token": gerar_token(usuario),
    }, status


@auth_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""
    if not email or not senha:
        return {"sucesso": False, "mensagem": "E-mail e senha são obrigatórios."}, 422

    usuario = Usuario.query.filter(func.lower(Usuario.email) == email.lower()).first()
    if not usuario or not usuario.verificar_senha(senha):
        return {"sucesso": False, "mensagem": "E-mail ou senha incorretos."}, 401
    return _resposta_auth(usuario)


@auth_bp.get("/me")
@requer_auth()
def me():
    usuario = db.session.get(Usuario, g.usuario_id)
    if not usuario:
        return {"sucesso": False, "mensagem": "Usuário não encontrado."}, 404
    return {"sucesso": True, "dados": _perfil_completo(usuario)}


@auth_bp.post("/register")
def register():
    dados = request.get_json(silent=True) or {}
    role = dados.get("tipoPerfil")
    required = ["nome", "email", "senha", "tipoPerfil"]
    missing = next((campo for campo in required if not dados.get(campo)), None)
    if missing:
        return {"sucesso": False, "mensagem": f"Campo obrigatório ausente: {missing}."}, 422
    if len(dados["senha"]) < MIN_SENHA:
        return {"sucesso": False,
                "mensagem": f"A senha deve ter ao menos {MIN_SENHA} caracteres."}, 422

    try:
        if not UsuarioService().email_disponivel(dados["email"]):
            raise ValueError(f"E-mail {dados['email']!r} já cadastrado.")
        if role == "Aluno":
            aluno_dados = dict(dados)
            aluno_dados["matricula"] = dados.get("matricula") or f"WEB{__import__('time').time_ns()}"
            aluno_dados.pop("progresso", None)  # progresso é calculado pelo sistema
            usuario = AlunoService().criar(aluno_dados)
        elif role == "Responsavel":
            usuario = ResponsavelService().criar(dados)
        elif role == "Professor":
            usuario = Professor.criar(
                nome=dados["nome"], email=dados["email"], senha=dados["senha"],
                tipoPerfil="Professor", formacao=dados.get("formacao"),
                disciplina=dados.get("disciplina"),
            )
        else:
            return {"sucesso": False, "mensagem": "Perfil inválido."}, 422
        return _resposta_auth(usuario, 201, "Conta criada.")
    except ValueError as exc:
        return {"sucesso": False, "mensagem": str(exc)}, 409


# ── RF03: recuperação de senha ───────────────────────────────────────────────
def _reset_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="adapteduca-reset")


def _marca_senha(usuario: Usuario) -> str:
    # O token carrega uma "impressão" da senha atual: após a troca, o link deixa de valer.
    return hashlib.sha256(usuario.senha.encode()).hexdigest()[:16]


@auth_bp.post("/esqueci-senha")
def esqueci_senha():
    email = ((request.get_json(silent=True) or {}).get("email") or "").strip()
    usuario = Usuario.query.filter(func.lower(Usuario.email) == email.lower()).first() if email else None
    if usuario:
        token = _reset_serializer().dumps({"id": usuario.id, "m": _marca_senha(usuario)})
        link = f"{current_app.config['FRONTEND_URL'].rstrip('/')}/redefinir-senha.html?token={token}"
        email_service.enviar(
            usuario.email, "AdaptEduca — redefinição de senha",
            f"Olá, {usuario.nome}!\n\nPara criar uma nova senha, acesse (o link vale por 1 hora):\n{link}\n\n"
            "Se você não pediu isso, ignore este e-mail.")
    # Resposta idêntica exista ou não a conta: não revela quais e-mails estão cadastrados.
    return {"sucesso": True, "mensagem": "Se o e-mail estiver cadastrado, enviaremos um link para redefinir a senha."}


@auth_bp.post("/redefinir-senha")
def redefinir_senha():
    dados = request.get_json(silent=True) or {}
    nova = dados.get("senha") or ""
    if len(nova) < MIN_SENHA:
        return {"sucesso": False, "mensagem": f"A senha deve ter ao menos {MIN_SENHA} caracteres."}, 422
    try:
        info = _reset_serializer().loads(
            dados.get("token") or "", max_age=current_app.config["RESET_TOKEN_MAX_AGE"])
    except SignatureExpired:
        return {"sucesso": False, "mensagem": "Este link expirou. Peça um novo."}, 400
    except BadSignature:
        return {"sucesso": False, "mensagem": "Link inválido."}, 400
    usuario = db.session.get(Usuario, info.get("id"))
    if not usuario or _marca_senha(usuario) != info.get("m"):
        return {"sucesso": False, "mensagem": "Este link já foi usado ou não é mais válido."}, 400
    usuario.senha = nova
    db.session.commit()
    return {"sucesso": True, "mensagem": "Senha redefinida. Entre com a nova senha."}
