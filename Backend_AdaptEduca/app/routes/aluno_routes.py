from flask import Blueprint
from app.controllers.aluno_controller import AlunoController
from app.security import requer_auth

aluno_bp = Blueprint("aluno", __name__, url_prefix="/api/alunos")
_ctrl = AlunoController()


# Rotas "me" vêm antes das rotas com <int:id>.
@aluno_bp.get("/me")
@requer_auth("Aluno")
def meu_perfil():
    return _ctrl.meu_perfil()


@aluno_bp.put("/me/questionario")
@requer_auth("Aluno")
def salvar_questionario():
    return _ctrl.salvar_questionario()


@aluno_bp.get("/")
@requer_auth("Professor")
def listar():
    return _ctrl.listar()


@aluno_bp.get("/<int:id>")
@requer_auth("Professor", proprio=True)
def buscar(id: int):
    return _ctrl.buscar(id)


@aluno_bp.post("/")
@requer_auth("Professor")
def criar():
    return _ctrl.criar()


@aluno_bp.put("/<int:id>")
@requer_auth(proprio=True)
def atualizar(id: int):
    return _ctrl.atualizar(id)


@aluno_bp.delete("/<int:id>")
@requer_auth(proprio=True)
def deletar(id: int):
    return _ctrl.deletar(id)


# ==========================================
# MODOS DE ESTUDO DO ALUNO
# ==========================================

from flask import g, request
from app.models.aluno import Aluno

MODOS_PERMITIDOS = {
    "leitura",
    "audio",
    "visual",
    "foco"
}


@aluno_bp.get("/me/modos-estudo")
@requer_auth("Aluno")
def consultar_modos_estudo():

    aluno = Aluno.buscar_por_id(g.usuario_id)

    if aluno is None:
        return {
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }, 404

    respostas = aluno.respostas_questionario()

    modos = respostas.get(
        "modosEstudo",
        []
    )

    if not isinstance(modos, list):
        modos = []

    return {
        "sucesso": True,
        "dados": {
            "modos": modos
        }
    }, 200


@aluno_bp.put("/me/modos-estudo")
@requer_auth("Aluno")
def salvar_modos_estudo():

    dados = request.get_json(silent=True) or {}

    modos = dados.get("modos")

    if not isinstance(modos, list):
        return {
            "sucesso": False,
            "mensagem": "Envie uma lista de modos."
        }, 422

    if (
        len(modos) > len(MODOS_PERMITIDOS)
        or len(set(str(m) for m in modos)) != len(modos)
        or any(
            not isinstance(m, str)
            or m not in MODOS_PERMITIDOS
            for m in modos
        )
    ):
        return {
            "sucesso": False,
            "mensagem": "Existem modos inválidos."
        }, 422

    aluno = Aluno.buscar_por_id(g.usuario_id)

    if aluno is None:
        return {
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }, 404

    respostas = aluno.respostas_questionario()

    # Preserva as outras respostas do questionário.
    respostas["modosEstudo"] = modos

    import json

    try:
        aluno.atualizar(
            questionario=json.dumps(
                respostas,
                ensure_ascii=False
            )
        )
    except Exception:
        return {
            "sucesso": False,
            "mensagem": "Não foi possível salvar os modos."
        }, 500

    return {
        "sucesso": True,
        "mensagem": "Modos salvos com sucesso.",
        "dados": {
            "modos": modos
        }
    }, 200


# ==========================================
# PREFERÊNCIAS DE APRENDIZAGEM DO ALUNO
# ==========================================

PREFERENCIAS_PERMITIDAS = {
    "videos": "Vídeos",
    "audios": "Áudios",
    "textos": "Resumos",
    "mapas": "Mapas Mentais",
    "etapas": "Atividades em Etapas"
}

PREFERENCIAS_INVERSAS = {
    valor: chave
    for chave, valor in PREFERENCIAS_PERMITIDAS.items()
}


# ==========================================
# CONSULTAR PREFERÊNCIAS SALVAS
# ==========================================

@aluno_bp.get("/me/preferencias")
@requer_auth("Aluno")
def consultar_preferencias():

    aluno = Aluno.buscar_por_id(g.usuario_id)

    if aluno is None:
        return {
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }, 404

    respostas = aluno.respostas_questionario()

    formatos = respostas.get("formats", [])

    if not isinstance(formatos, list):
        formatos = []

    preferencias = [
        PREFERENCIAS_INVERSAS[formato]
        for formato in formatos
        if formato in PREFERENCIAS_INVERSAS
    ]

    return {
        "sucesso": True,
        "dados": {
            "preferencias": preferencias
        }
    }, 200


# ==========================================
# SALVAR PREFERÊNCIAS NO MYSQL
# ==========================================

@aluno_bp.put("/me/preferencias")
@requer_auth("Aluno")
def salvar_preferencias():

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return {
            "sucesso": False,
            "mensagem": "Envie um JSON válido."
        }, 400

    preferencias = dados.get("preferencias")

    # Verificar se a lista é válida.
    if (
        not isinstance(preferencias, list)
        or not preferencias
        or len(preferencias) > len(PREFERENCIAS_PERMITIDAS)
        or any(
            not isinstance(item, str)
            or item not in PREFERENCIAS_PERMITIDAS
            for item in preferencias
        )
        or len(preferencias) != len(set(preferencias))
    ):
        return {
            "sucesso": False,
            "mensagem": "Selecione preferências válidas."
        }, 422

    aluno = Aluno.buscar_por_id(g.usuario_id)

    if aluno is None:
        return {
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }, 404

    respostas = aluno.respostas_questionario()

    # Preserva formatos escolhidos no questionário
    # que não aparecem na página de demonstração.
    formatos_anteriores = respostas.get("formats", [])

    if not isinstance(formatos_anteriores, list):
        formatos_anteriores = []

    formatos_extras = [
        item
        for item in formatos_anteriores
        if item not in PREFERENCIAS_INVERSAS
    ]

    novos_formatos = [
        PREFERENCIAS_PERMITIDAS[item]
        for item in preferencias
    ]

    formatos = formatos_extras + novos_formatos

    # Atualiza somente as preferências,
    # mantendo o restante do questionário.
    respostas["formats"] = formatos

    try:
        import json

        aluno.atualizar(
            questionario=json.dumps(
                respostas,
                ensure_ascii=False
            ),
            preferenciaAprendizagem=(
                ", ".join(formatos)[:80]
            )
        )

    except Exception:
        return {
            "sucesso": False,
            "mensagem": "Erro ao salvar preferências."
        }, 500

    return {
        "sucesso": True,
        "mensagem": "Preferências salvas com sucesso!",
        "dados": {
            "preferencias": preferencias
        }
    }, 200
