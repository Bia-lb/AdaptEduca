from typing import List, Optional

from app.models.responsavel import Responsavel
from app.models.aluno import Aluno
from app.models.resposta import Resposta


class ResponsavelService:
    def listar(self) -> List[Responsavel]:
        return Responsavel.listar()

    def buscar(self, id: int) -> Optional[Responsavel]:
        return Responsavel.buscar_por_id(id)

    def criar(self, dados: dict) -> Responsavel:
        return Responsavel.criar(
            nome=dados["nome"], email=dados["email"], senha=dados["senha"],
            tipoPerfil="Responsavel", parentesco=dados.get("parentesco"),
            telefone=dados.get("telefone"),
        )

    def atualizar(self, id: int, dados: dict) -> Responsavel:
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")
        permitido = {k: v for k, v in dados.items()
                     if k in ("nome", "email", "senha", "parentesco", "telefone")}
        return responsavel.atualizar(**permitido)

    def deletar(self, id: int) -> None:
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")
        responsavel.deletar()

    def dashboard(self, id: int) -> dict:
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")

        alunos: List[Aluno] = list(responsavel.filhos)

        progresso_medio = round(
            sum(a.progresso for a in alunos) / len(alunos), 1
        ) if alunos else 0.0

        alunos_data = []
        for aluno in alunos:
            atividades = [atividade for turma in aluno.turmas for atividade in turma.atividades]
            enviadas = {
                r.atividade_id for r in Resposta.query.filter_by(
                    aluno_id=aluno.id, status="Enviada")
            }
            concluidas = sum(1 for a in atividades if a.id in enviadas)
            em_andamento = len(atividades) - concluidas
            proxima_aula = next(({"titulo": t.nome, "horario": "—"} for t in aluno.turmas), None)
            alunos_data.append({
                "id": aluno.id, "nome": aluno.nome, "progresso": aluno.progresso,
                "matricula": aluno.matricula,
                "preferenciaAprendizagem": aluno.preferenciaAprendizagem,
                "atividadesConcluidas": concluidas, "emAndamento": em_andamento,
                "proximaAula": proxima_aula,
            })

        return {
            "responsavel": responsavel.to_dict(),
            "totalFilhos": len(alunos),
            "progressoMedio": progresso_medio,
            "alunos": alunos_data,
        }

    # ── vínculo responsável ↔ aluno (RF19) ──────────────────────────────────
    def vincular_filho(self, id: int, matricula: str, email: str) -> Aluno:
        """O vínculo exige matrícula E e-mail do aluno, para evitar acompanhar
        crianças de terceiros por tentativa e erro."""
        from app import db
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError("Responsável não encontrado.")
        aluno = Aluno.query.filter_by(matricula=(matricula or "").strip()).first()
        if not aluno or aluno.email.lower() != (email or "").strip().lower():
            raise LookupError("Não encontramos um aluno com essa matrícula e e-mail.")
        if aluno in responsavel.filhos:
            raise ValueError("Este aluno já está vinculado a você.")
        responsavel.filhos.append(aluno)
        db.session.commit()
        return aluno

    def desvincular_filho(self, id: int, aluno_id: int) -> None:
        from app import db
        responsavel = Responsavel.buscar_por_id(id)
        aluno = Aluno.buscar_por_id(aluno_id)
        if not responsavel or not aluno or aluno not in responsavel.filhos:
            raise LookupError("Aluno não está vinculado.")
        responsavel.filhos.remove(aluno)
        db.session.commit()
