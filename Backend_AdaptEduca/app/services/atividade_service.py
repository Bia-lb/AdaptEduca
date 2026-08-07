from datetime import date
from typing import List, Optional
from app.models.atividade import Atividade
from app.repositories.atividade_repository import AtividadeRepository


class AtividadeService:
    def __init__(self) -> None:
        self._repo = AtividadeRepository()

    def listar(self) -> List[Atividade]:
        return self._repo.listar_todos()

    def buscar(self, id: int) -> Optional[Atividade]:
        return self._repo.buscar_por_id(id)

    def listar_por_turma(self, turma_id: int) -> List[Atividade]:
        return self._repo.listar_por_turma(turma_id)

    def criar(self, dados: dict) -> Atividade:
        prazo = None
        if dados.get("prazo"):
            prazo = date.fromisoformat(dados["prazo"])

        atividade = Atividade(
            titulo=dados["titulo"],
            descricao=dados.get("descricao"),
            prazo=prazo,
            status=dados.get("status", "Pendente"),
            turma_id=dados["turma_id"],
        )
        return self._repo.salvar(atividade)

    def atualizar(self, id: int, dados: dict) -> Atividade:
        atividade = self._repo.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")

        atividade.titulo = dados.get("titulo", atividade.titulo)
        atividade.descricao = dados.get("descricao", atividade.descricao)
        atividade.status = dados.get("status", atividade.status)
        if dados.get("prazo"):
            atividade.prazo = date.fromisoformat(dados["prazo"])

        return self._repo.salvar(atividade)

    def deletar(self, id: int) -> None:
        atividade = self._repo.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")
        self._repo.deletar(atividade)
