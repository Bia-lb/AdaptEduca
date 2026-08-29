from datetime import date
from typing import List, Optional

from app.models.atividade import Atividade
from app.repositories.atividade_repository import AtividadeRepository


class AtividadeService:
    def __init__(self) -> None:
        self._repo = AtividadeRepository()

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

    def criar(self, dados: dict) -> Atividade:
        prazo = date.fromisoformat(dados["prazo"]) if dados.get("prazo") else None
        return Atividade.criar(
            titulo=dados["titulo"], descricao=dados.get("descricao"), prazo=prazo,
            status=dados.get("status", "Pendente"), turma_id=dados["turma_id"]
        )

    def atualizar(self, id: int, dados: dict) -> Atividade:
        atividade = Atividade.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")
        if "prazo" in dados:
            dados["prazo"] = date.fromisoformat(dados["prazo"]) if dados["prazo"] else None
        return atividade.atualizar(**dados)

    def deletar(self, id: int) -> None:
        atividade = Atividade.buscar_por_id(id)
        if not atividade:
            raise LookupError(f"Atividade {id} não encontrada.")
        atividade.deletar()
