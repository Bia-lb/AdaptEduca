import json
from datetime import date, datetime, timezone
from typing import List, Optional

from app import db
from app.models.aluno import Aluno
from app.models.atividade import Atividade
from app.models.feedback import Feedback
from app.models.resposta import Resposta
from app.models.turma import Turma
from app.repositories.atividade_repository import AtividadeRepository
from app.services.turma_service import TurmaService

CAMPOS_EDITAVEIS = ("titulo", "descricao", "prazo", "questoes", "etapas")


def _parse_prazo(valor):
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError("Prazo inválido. Use o formato AAAA-MM-DD.")


def _normalizar_questoes(valor) -> Optional[str]:
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.splitlines()
    if not isinstance(valor, list):
        raise ValueError("As questões devem ser uma lista de textos.")
    limpas = [str(q).strip() for q in valor if str(q).strip()]
    return json.dumps(limpas, ensure_ascii=False)


def _normalizar_etapas(valor) -> Optional[str]:
    """Aceita lista de {titulo, instrucao} ou texto com uma etapa por linha
    ("Título: instrução" ou apenas "Título")."""
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.splitlines()
    if not isinstance(valor, list):
        raise ValueError("As etapas devem ser uma lista.")
    etapas = []
    for item in valor:
        if isinstance(item, dict):
            titulo, instrucao = str(item.get("titulo", "")).strip(), str(item.get("instrucao", "")).strip()
        else:
            titulo, _, instrucao = str(item).partition(":")
            titulo, instrucao = titulo.strip(), instrucao.strip()
        if titulo:
            etapas.append({"titulo": titulo[:120], "instrucao": instrucao})
    return json.dumps(etapas, ensure_ascii=False)


class AtividadeService:
    def __init__(self) -> None:
        self._repo = AtividadeRepository()
        self._turmas = TurmaService()

    def listar(self) -> List[Atividade]:
        return Atividade.listar()

    def buscar(self, id: int) -> Optional[Atividade]:
        return Atividade.buscar_por_id(id)

    def listar_por_turma(self, turma_id: int) -> List[Atividade]:
        ids = self._repo.listar_ids_por_turma(turma_id)
        atividades = []
        for atividade_id in ids:
            atividade = Atividade.buscar_por_id(atividade_id)
            if atividade:
                atividades.append(atividade)
        return atividades

    def listar_para(self, usuario_id: int, perfil: str) -> List[dict]:
        """Atividades visíveis ao usuário, já no formato de resposta da API."""
        turmas = self._turmas.listar_para(usuario_id, perfil)
        atividades = [a for t in turmas for a in self.listar_por_turma(t.id)]
        nomes = {t.id: t.nome for t in turmas}
        saida = []
        for atividade in atividades:
            item = atividade.to_dict()
            item["turmaNome"] = nomes.get(atividade.turma_id)
            if perfil == "Aluno":
                resposta = self.resposta_do_aluno(atividade.id, usuario_id)
                item["minhaResposta"] = resposta.to_dict() if resposta else None
                item["status"] = "Concluida" if resposta and resposta.status == "Enviada" else "Pendente"
                item["nota"] = resposta.nota if resposta else None
                item["feedbacks"] = [
                    {"tipo": f.tipo, "mensagem": f.mensagem, "data": f.data.isoformat() if f.data else None}
                    for f in Feedback.query.filter_by(atividade_id=atividade.id, aluno_id=usuario_id)
                    .order_by(Feedback.id.desc())]
            elif perfil == "Professor":
                total = len(atividade.turma.alunos)
                enviadas = Resposta.query.filter_by(
                    atividade_id=atividade.id, status="Enviada").count()
                item["totalAlunos"] = total
                item["totalEnviadas"] = enviadas
            saida.append(item)
        return saida

    def criar(self, dados: dict, professor_id: int) -> Atividade:
        turma = Turma.buscar_por_id(dados["turma_id"])
        if not turma or turma.professor_id != professor_id:
            raise PermissionError("Você só pode criar atividades nas suas turmas.")
        titulo = str(dados["titulo"]).strip()
        if not titulo:
            raise ValueError("O título é obrigatório.")
        return Atividade.criar(
            titulo=titulo, descricao=dados.get("descricao"),
            prazo=_parse_prazo(dados.get("prazo")),
            questoes=_normalizar_questoes(dados.get("questoes")),
            etapas=_normalizar_etapas(dados.get("etapas")),
            status="Pendente", turma_id=turma.id,
        )

    def atualizar(self, id: int, dados: dict) -> Atividade:
        atividade = Atividade.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")
        campos = {k: v for k, v in dados.items() if k in CAMPOS_EDITAVEIS}
        if "prazo" in campos:
            campos["prazo"] = _parse_prazo(campos["prazo"])
        if "questoes" in campos:
            campos["questoes"] = _normalizar_questoes(campos["questoes"])
        if "etapas" in campos:
            campos["etapas"] = _normalizar_etapas(campos["etapas"])
        return atividade.atualizar(**campos)

    def deletar(self, id: int) -> None:
        atividade = Atividade.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")
        atividade.deletar()

    # ── respostas do aluno (RF15) ───────────────────────────────────────────
    @staticmethod
    def resposta_do_aluno(atividade_id: int, aluno_id: int) -> Optional[Resposta]:
        return Resposta.query.filter_by(atividade_id=atividade_id, aluno_id=aluno_id).first()

    def salvar_resposta(self, atividade: Atividade, aluno_id: int, respostas,
                        enviar: bool, etapas_concluidas=None) -> Resposta:
        aluno = Aluno.buscar_por_id(aluno_id)
        if aluno is None or atividade.turma not in aluno.turmas.all():
            raise PermissionError("Esta atividade não pertence a nenhuma das suas turmas.")
        resposta = self.resposta_do_aluno(atividade.id, aluno_id)
        if resposta and resposta.status == "Enviada":
            raise ValueError("Esta atividade já foi enviada e não pode ser alterada.")

        total_q = len(atividade.lista_questoes())
        total_e = len(atividade.lista_etapas())
        if respostas is None:
            respostas = resposta.lista_respostas() if resposta else []
        if not isinstance(respostas, list):
            raise ValueError("As respostas devem ser uma lista de textos.")
        respostas = [str(r) for r in respostas]
        if total_q and respostas and len(respostas) != total_q:
            raise ValueError(f"Esperadas {total_q} respostas, recebidas {len(respostas)}.")
        if etapas_concluidas is None:
            etapas_concluidas = resposta.lista_etapas_concluidas() if resposta else []
        try:
            etapas_concluidas = sorted({int(i) for i in etapas_concluidas})
        except (TypeError, ValueError):
            raise ValueError("Etapas inválidas.")
        if any(i < 0 or i >= total_e for i in etapas_concluidas):
            raise ValueError("Etapa inexistente.")

        if enviar:
            if total_q and (len(respostas) != total_q or any(not r.strip() for r in respostas)):
                raise ValueError("Responda todas as questões antes de enviar.")
            if total_e and len(etapas_concluidas) != total_e:
                raise ValueError("Conclua todas as etapas antes de enviar.")

        if resposta is None:
            resposta = Resposta(atividade_id=atividade.id, aluno_id=aluno_id)
            db.session.add(resposta)
        resposta.respostas = json.dumps(respostas, ensure_ascii=False)
        resposta.etapasConcluidas = json.dumps(etapas_concluidas)
        if enviar:
            resposta.status = "Enviada"
            resposta.enviadaEm = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            resposta.status = "Em andamento"
        db.session.flush()
        self.recalcular_progresso(aluno)
        db.session.commit()
        return resposta

    @staticmethod
    def recalcular_progresso(aluno: Aluno) -> float:
        """Progresso = atividades enviadas / atividades das turmas do aluno."""
        ids = [a.id for t in aluno.turmas.all() for a in t.atividades]
        if not ids:
            aluno.progresso = 0.0
            return 0.0
        enviadas = Resposta.query.filter(
            Resposta.aluno_id == aluno.id, Resposta.status == "Enviada",
            Resposta.atividade_id.in_(ids)).count()
        aluno.progresso = round(enviadas / len(ids) * 100, 1)
        return aluno.progresso

    def listar_respostas(self, atividade: Atividade) -> List[dict]:
        saida = []
        for aluno in atividade.turma.alunos:
            r = self.resposta_do_aluno(atividade.id, aluno.id)
            saida.append({
                "aluno_id": aluno.id, "aluno": aluno.nome,
                "status": r.status if r else "Não iniciada",
                "respostas": r.lista_respostas() if r else [],
                "etapasConcluidas": r.lista_etapas_concluidas() if r else [],
                "nota": r.nota if r else None,
                "feedbacks": [
                    {"id": f.id, "tipo": f.tipo, "mensagem": f.mensagem,
                     "data": f.data.isoformat() if f.data else None}
                    for f in Feedback.query.filter_by(atividade_id=atividade.id, aluno_id=aluno.id)
                    .order_by(Feedback.id.desc())],
                "enviadaEm": r.enviadaEm.isoformat() if r and r.enviadaEm else None,
            })
        return saida
