from typing import List, Optional

from app.models.responsavel import Responsavel
from app.models.aluno import Aluno


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
        return responsavel.atualizar(**dados)

    def deletar(self, id: int) -> None:
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")
        responsavel.deletar()

    def dashboard(self, id: int) -> dict:
        responsavel = Responsavel.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")

        alunos: List[Aluno] = []
        for turma in responsavel.turmas:
            alunos.extend(turma.alunos)
        alunos = list({a.id: a for a in alunos}.values())

        progresso_medio = round(
            sum(a.progresso for a in alunos) / len(alunos), 1
        ) if alunos else 0.0

        alunos_data = []
        for aluno in alunos:
            atividades = [atividade for turma in aluno.turmas for atividade in turma.atividades]
            concluidas = sum(1 for a in atividades if a.status == "Concluida")
            em_andamento = sum(1 for a in atividades if a.status == "Pendente")
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
