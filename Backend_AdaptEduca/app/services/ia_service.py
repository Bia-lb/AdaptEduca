"""Camada de acesso à IA (Anthropic / Claude).

Responsabilidades: cliente, cota diária por usuário, timeout, chamadas simples
e com ferramentas (tool use), extração/validação de JSON. A chave da API vem
apenas de variável de ambiente do servidor e nunca é enviada ao navegador.

Para testes, um cliente falso pode ser injetado em
`app.extensions["ia_client"]` (mesma interface de `anthropic.Anthropic`).
"""
import json
import re
import threading
import time
from datetime import date
from typing import Callable, List, Optional

from flask import current_app

from app import db
from app.models.ia_uso import IAUso


class IAIndisponivel(Exception):
    """IA não configurada (sem chave) ou temporariamente fora do ar."""


class IACotaExcedida(Exception):
    """Usuário atingiu o limite diário de chamadas."""


class IAFalha(Exception):
    """A IA respondeu algo inutilizável ou a chamada falhou."""


# Se a API falhar, evita insistir a cada requisição por alguns segundos.
_PAUSA_APOS_FALHA = 45
_falha_em = 0.0
_lock = threading.Lock()


def _registrar_falha() -> None:
    global _falha_em
    with _lock:
        _falha_em = time.monotonic()


def _em_pausa() -> bool:
    return (time.monotonic() - _falha_em) < _PAUSA_APOS_FALHA


def resetar_pausa() -> None:  # usado nos testes
    global _falha_em
    _falha_em = 0.0


def _cliente():
    injetado = current_app.extensions.get("ia_client")
    if injetado is not None:
        return injetado
    chave = current_app.config.get("ANTHROPIC_API_KEY")
    if not chave:
        return None
    cache = current_app.extensions.setdefault("ia_client_real", {})
    if "c" not in cache:
        import anthropic
        cache["c"] = anthropic.Anthropic(
            api_key=chave, timeout=current_app.config["IA_TIMEOUT"], max_retries=1)
    return cache["c"]


def disponivel() -> bool:
    return _cliente() is not None and not _em_pausa()


def restante(usuario_id: int) -> int:
    limite = current_app.config["IA_LIMITE_DIARIO"]
    uso = IAUso.query.filter_by(usuario_id=usuario_id, dia=date.today()).first()
    return max(0, limite - (uso.quantidade if uso else 0))


def _consumir(usuario_id: int) -> None:
    limite = current_app.config["IA_LIMITE_DIARIO"]
    uso = IAUso.query.filter_by(usuario_id=usuario_id, dia=date.today()).first()
    if uso is None:
        uso = IAUso(usuario_id=usuario_id, dia=date.today(), quantidade=0)
        db.session.add(uso)
    if uso.quantidade >= limite:
        db.session.rollback()
        raise IACotaExcedida(f"Você atingiu o limite de {limite} usos da IA por hoje. Tente novamente amanhã.")
    uso.quantidade += 1
    db.session.commit()


# ── texto / JSON ──────────────────────────────────────────────────────────────
def _texto(resposta) -> str:
    return "".join(getattr(b, "text", "") for b in resposta.content if getattr(b, "type", "") == "text").strip()


def extrair_json(texto: str) -> dict:
    """Aceita JSON puro, com cercas ``` ou com texto ao redor."""
    texto = (texto or "").strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.I)
    try:
        valor = json.loads(texto)
    except ValueError:
        ini, fim = texto.find("{"), texto.rfind("}")
        if ini < 0 or fim <= ini:
            raise IAFalha("A IA não devolveu um JSON.")
        try:
            valor = json.loads(texto[ini:fim + 1])
        except ValueError:
            raise IAFalha("A IA devolveu um JSON inválido.")
    if not isinstance(valor, dict):
        raise IAFalha("A IA devolveu um formato inesperado.")
    return valor


def _criar(**args):
    cliente = _cliente()
    if cliente is None or _em_pausa():
        raise IAIndisponivel("O assistente de IA não está disponível no momento.")
    try:
        return cliente.messages.create(model=current_app.config["ANTHROPIC_MODEL"], **args)
    except IAIndisponivel:
        raise
    except Exception as exc:  # erros de rede, 429/5xx da API, timeout...
        current_app.logger.warning("Falha na API de IA: %s", type(exc).__name__)
        _registrar_falha()
        raise IAFalha("Não foi possível falar com a IA agora.")


# ── chamadas de alto nível ────────────────────────────────────────────────────
def conversar(usuario_id: int, system: str, mensagens: List[dict], max_tokens: int = 700) -> str:
    _consumir(usuario_id)
    resposta = _criar(system=system, messages=mensagens, max_tokens=max_tokens)
    texto = _texto(resposta)
    if not texto:
        raise IAFalha("A IA não devolveu texto.")
    return texto


def gerar_json(usuario_id: int, system: str, usuario: str, validador: Callable[[dict], dict],
               max_tokens: int = 3000) -> dict:
    """Uma chamada que deve devolver JSON; `validador` normaliza ou levanta ValueError."""
    _consumir(usuario_id)
    resposta = _criar(system=system, messages=[{"role": "user", "content": usuario}], max_tokens=max_tokens)
    try:
        return validador(extrair_json(_texto(resposta)))
    except ValueError as exc:
        raise IAFalha(str(exc))


def agente_com_ferramentas(usuario_id: int, system: str, pedido: str, ferramentas: List[dict],
                           executor: Callable[[str, dict], object], validador: Callable[[dict], dict],
                           max_voltas: int = 6, max_tokens: int = 2000) -> dict:
    """Laço de tool use: o modelo consulta ferramentas (executadas no servidor)
    até produzir a resposta final em JSON. Conta como UMA unidade de cota."""
    _consumir(usuario_id)
    mensagens = [{"role": "user", "content": pedido}]
    for _ in range(max_voltas):
        resposta = _criar(system=system, messages=mensagens, max_tokens=max_tokens, tools=ferramentas)
        if resposta.stop_reason != "tool_use":
            try:
                return validador(extrair_json(_texto(resposta)))
            except ValueError as exc:
                raise IAFalha(str(exc))
        blocos, resultados = [], []
        for b in resposta.content:
            if b.type == "text":
                blocos.append({"type": "text", "text": b.text})
            elif b.type == "tool_use":
                blocos.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
                try:
                    saida = executor(b.name, b.input if isinstance(b.input, dict) else {})
                    resultados.append({"type": "tool_result", "tool_use_id": b.id,
                                       "content": json.dumps(saida, ensure_ascii=False, default=str)})
                except Exception as exc:
                    resultados.append({"type": "tool_result", "tool_use_id": b.id, "is_error": True,
                                       "content": f"Erro: {exc}"})
        mensagens.append({"role": "assistant", "content": blocos})
        mensagens.append({"role": "user", "content": resultados})
    raise IAFalha("A IA demorou demais para concluir a análise.")
