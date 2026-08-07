from typing import List, Optional
from app.models.responsavel import Responsavel
from app.models.aluno import Aluno
from app.repositories.responsavel_repository import ResponsavelRepository
from app.repositories.aluno_repository import AlunoRepository
from app import db


class ResponsavelService:
    def __init__(self) -> None:
        self._repo = ResponsavelRepository()
        self._aluno_repo = AlunoRepository()

    def listar(self) -> List[Responsavel]:
        return self._repo.listar_todos()

    def buscar(self, id: int) -> Optional[Responsavel]:
        return self._repo.buscar_por_id(id)

    def criar(self, dados: dict) -> Responsavel:
        responsavel = Responsavel(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            tipoPerfil="Responsavel",
            parentesco=dados.get("parentesco"),
            telefone=dados.get("telefone"),
        )
        return self._repo.salvar(responsavel)

    def atualizar(self, id: int, dados: dict) -> Responsavel:
        responsavel = self._repo.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")

        responsavel.nome = dados.get("nome", responsavel.nome)
        responsavel.email = dados.get("email", responsavel.email)
        responsavel.parentesco = dados.get("parentesco", responsavel.parentesco)
        responsavel.telefone = dados.get("telefone", responsavel.telefone)
        return self._repo.salvar(responsavel)

    def deletar(self, id: int) -> None:
        responsavel = self._repo.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")
        self._repo.deletar(responsavel)

    def dashboard(self, id: int) -> dict:
        """
        Agrega dados para o dashboard do Responsável
        (replica o que o mockup exibe).
        """
        responsavel = self._repo.buscar_por_id(id)
        if not responsavel:
            raise LookupError(f"Responsável {id} não encontrado.")

        # Alunos das turmas do responsável (filhos cadastrados)
        alunos: List[Aluno] = []
        for turma in responsavel.turmas:
            alunos.extend(turma.alunos)

        # Remove duplicatas (aluno em mais de uma turma)
        alunos = list({a.id: a for a in alunos}.values())

        progresso_medio = (
            round(sum(a.progresso for a in alunos) / len(alunos), 1)
            if alunos else 0.0
        )

        alunos_data = []
        for aluno in alunos:
            atividades = []
            for turma in aluno.turmas:
                atividades.extend(turma.atividades)

            concluidas = sum(1 for a in atividades if a.status == "Concluida")
            em_andamento = sum(1 for a in atividades if a.status == "Pendente")

            proxima_aula = next(
                (
                    {"titulo": t.nome, "horario": "—"}
                    for t in aluno.turmas
                ), None
            )

            alunos_data.append({
                "id": aluno.id,
                "nome": aluno.nome,
                "progresso": aluno.progresso,
                "matricula": aluno.matricula,
                "preferenciaAprendizagem": aluno.preferenciaAprendizagem,
                "atividadesConcluidas": concluidas,
                "emAndamento": em_andamento,
                "proximaAula": proxima_aula,
            })

        return {
            "responsavel": responsavel.to_dict(),
            "totalFilhos": len(alunos),
            "progressoMedio": progresso_medio,
            "alunos": alunos_data,
        }
