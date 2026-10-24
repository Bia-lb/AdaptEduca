"""Progresso, desempenho e relatórios (RF16, RF17, RF19, RF20) calculados dos
registros reais: respostas, notas, prazos e sessões de estudo."""
import json
import math
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

from app import db
from app.models.aluno import Aluno
from app.models.relatorio import Relatorio
from app.models.resposta import Resposta
from app.models.sessao_estudo import SessaoEstudo

NOTA_MINIMA = 6.0


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def classificar(valor: Optional[float]) -> str:
    if valor is None:
        return "Sem dados"
    if valor >= 85:
        return "Excelente"
    if valor >= 70:
        return "Bom desempenho"
    if valor >= 50:
        return "Acompanhar"
    return "Precisa de atenção"


def _media(valores: List[float]) -> Optional[float]:
    return round(sum(valores) / len(valores), 2) if valores else None


def _inicio_semana(d: date) -> date:
    return d - timedelta(days=d.weekday())


class ProgressoService:
    # ── permissões ─────────────────────────────────────────────────────────
    def pode_ver_aluno(self, usuario_id: int, perfil: str, aluno: Aluno) -> bool:
        if perfil == "Aluno":
            return aluno.id == usuario_id
        if perfil == "Professor":
            return any(t.professor_id == usuario_id for t in aluno.turmas.all())
        if perfil == "Responsavel":
            return any(r.id == usuario_id for r in _responsaveis_do_aluno(aluno))
        return False

    # ── relatório de um aluno ──────────────────────────────────────────────
    def relatorio_aluno(self, aluno: Aluno, dias: int = 30) -> dict:
        dias = max(7, min(int(dias), 365))
        hoje = date.today()
        desde = _agora() - timedelta(days=dias)
        respostas: Dict[int, Resposta] = {
            r.atividade_id: r for r in Resposta.query.filter_by(aluno_id=aluno.id)}
        sessoes = SessaoEstudo.query.filter(
            SessaoEstudo.aluno_id == aluno.id, SessaoEstudo.iniciadaEm >= desde).all()

        materias: Dict[str, dict] = {}
        total = enviadas = atrasadas = 0
        notas_todas: List[float] = []
        proximas = []
        for turma in aluno.turmas.all():
            nome = (turma.professor.disciplina or turma.nome) if turma.professor else turma.nome
            m = materias.setdefault(nome, {"materia": nome, "atividades": 0, "enviadas": 0,
                                           "atrasadas": 0, "notas": []})
            for a in turma.atividades:
                total += 1
                m["atividades"] += 1
                r = respostas.get(a.id)
                if r and r.status == "Enviada":
                    enviadas += 1
                    m["enviadas"] += 1
                    if r.nota is not None:
                        m["notas"].append(r.nota)
                        notas_todas.append(r.nota)
                else:
                    if a.prazo and a.prazo < hoje:
                        atrasadas += 1
                        m["atrasadas"] += 1
                    else:
                        proximas.append({"id": a.id, "titulo": a.titulo, "prazo": a.prazo.isoformat() if a.prazo else None,
                                         "materia": nome})
        proximas.sort(key=lambda x: x["prazo"] or "9999")

        lista_materias, dificeis = [], []
        for m in materias.values():
            media = _media(m.pop("notas"))
            m["mediaNota"] = media
            lista_materias.append(m)
            ratio = m["enviadas"] / m["atividades"] if m["atividades"] else 1
            if (media is not None and media < NOTA_MINIMA) or (m["atrasadas"] and ratio < 0.5):
                dificeis.append(m["materia"])
        declarada = aluno.respostas_questionario().get("dificuldade")

        progresso = round(enviadas / total * 100, 1) if total else 0.0
        media_nota = _media(notas_todas)
        desempenho = round(media_nota * 10, 1) if media_nota is not None else None
        segundos = sum(s.segundos for s in sessoes)

        # evolução semanal
        semanas = math.ceil(dias / 7)
        base = _inicio_semana(hoje) - timedelta(weeks=semanas - 1)
        evolucao = []
        for i in range(semanas):
            ini = base + timedelta(weeks=i)
            fim = ini + timedelta(days=7)
            env = [r for r in respostas.values() if r.status == "Enviada" and r.enviadaEm
                   and ini <= r.enviadaEm.date() < fim]
            notas = [r.nota for r in env if r.nota is not None]
            seg = sum(s.segundos for s in sessoes if ini <= s.iniciadaEm.date() < fim)
            evolucao.append({"semana": ini.isoformat(), "atividadesEnviadas": len(env),
                             "minutosEstudo": round(seg / 60), "mediaNota": _media(notas)})

        por_modo: Dict[str, int] = {}
        for s in sessoes:
            por_modo[s.modo] = por_modo.get(s.modo, 0) + s.segundos

        return {
            "aluno": {"id": aluno.id, "nome": aluno.nome, "matricula": aluno.matricula},
            "periodoDias": dias, "geradoEm": _agora().isoformat(timespec="seconds"),
            "progresso": progresso, "desempenho": desempenho,
            "status": classificar(desempenho if desempenho is not None else progresso),
            "atividades": {"total": total, "enviadas": enviadas, "pendentes": total - enviadas,
                           "atrasadas": atrasadas},
            "mediaNota": media_nota,
            "tempoEstudoMinutos": round(segundos / 60),
            "tempoPorModo": {k: round(v / 60) for k, v in por_modo.items()},
            "sessoes": len(sessoes),
            "materias": sorted(lista_materias, key=lambda x: x["materia"]),
            "materiasDificeis": dificeis, "dificuldadeDeclarada": declarada,
            "evolucao": evolucao, "proximasAtividades": proximas[:5],
        }

    def sincronizar_progresso(self, aluno: Aluno) -> None:
        from app.services.atividade_service import AtividadeService
        AtividadeService.recalcular_progresso(aluno)

    # ── professor (RF17) ───────────────────────────────────────────────────
    def dashboard_professor(self, professor_id: int, dias: int = 30) -> dict:
        from app.models.turma import Turma
        turmas = Turma.query.filter_by(professor_id=professor_id).order_by(Turma.nome).all()
        alunos: Dict[int, Aluno] = {}
        for t in turmas:
            for a in t.alunos:
                alunos[a.id] = a
        linhas = []
        agregado: Dict[str, dict] = {}
        total_enviadas = 0
        for a in alunos.values():
            r = self.relatorio_aluno(a, dias)
            total_enviadas += r["atividades"]["enviadas"]
            for m in r["materias"]:
                g = agregado.setdefault(m["materia"], {"materia": m["materia"], "atividades": 0, "enviadas": 0, "notas": []})
                g["atividades"] += m["atividades"]
                g["enviadas"] += m["enviadas"]
                if m["mediaNota"] is not None:
                    g["notas"].append(m["mediaNota"])
            linhas.append({
                "id": a.id, "nome": a.nome, "matricula": a.matricula,
                "turmas": [t.nome for t in a.turmas.all() if t.professor_id == professor_id],
                "progresso": r["progresso"], "desempenho": r["desempenho"], "status": r["status"],
                "atrasadas": r["atividades"]["atrasadas"], "tempoEstudoMinutos": r["tempoEstudoMinutos"],
                "materiasDificeis": r["materiasDificeis"],
            })
        linhas.sort(key=lambda x: (x["desempenho"] if x["desempenho"] is not None else x["progresso"]))
        validos = [x["desempenho"] for x in linhas if x["desempenho"] is not None]
        ativ_total = sum(len(t.atividades) for t in turmas)
        return {
            "totalTurmas": len(turmas), "totalAlunos": len(linhas), "totalAtividades": ativ_total,
            "progressoMedio": _media([x["progresso"] for x in linhas]) or 0.0,
            "desempenhoMedio": _media(validos),
            "alunosEmAtencao": [x for x in linhas if x["status"] == "Precisa de atenção" or x["atrasadas"] > 0],
            "alunos": linhas, "periodoDias": max(7, min(int(dias), 365)),
            "atividadesEnviadas": total_enviadas,
            "tempoMedioEstudoMinutos": round(sum(x["tempoEstudoMinutos"] for x in linhas) / len(linhas)) if linhas else 0,
            "porMateria": [{"materia": g["materia"], "atividades": g["atividades"], "enviadas": g["enviadas"],
                            "mediaNota": _media(g["notas"])} for g in agregado.values()],
            "turmas": [{"id": t.id, "nome": t.nome, "totalAlunos": len(t.alunos)} for t in turmas],
        }

    # ── responsável (RF19) ─────────────────────────────────────────────────
    def painel_responsavel(self, responsavel) -> dict:
        filhos = [self.relatorio_aluno(a, 30) for a in responsavel.filhos]
        return {
            "responsavel": responsavel.to_dict(),
            "totalFilhos": len(filhos),
            "progressoMedio": _media([f["progresso"] for f in filhos]) or 0.0,
            "filhos": filhos,
        }

    # ── relatórios salvos (RF20) ───────────────────────────────────────────
    def salvar_relatorio(self, aluno: Aluno, dias: int) -> Relatorio:
        dados = self.relatorio_aluno(aluno, dias)
        rel = Relatorio(
            aluno_id=aluno.id,
            desempenho=dados["desempenho"] if dados["desempenho"] is not None else dados["progresso"],
            tempoEstudo=round(dados["tempoEstudoMinutos"] / 60, 2),
            materiasDificeis=", ".join(dados["materiasDificeis"])[:255] or None,
            periodo=f"Últimos {dados['periodoDias']} dias",
            geradoEm=_agora(), dados=json.dumps(dados, ensure_ascii=False))
        db.session.add(rel)
        db.session.commit()
        return rel


def _responsaveis_do_aluno(aluno: Aluno):
    from app.models.responsavel import Responsavel
    return [r for r in Responsavel.query.all() if aluno in r.filhos]
