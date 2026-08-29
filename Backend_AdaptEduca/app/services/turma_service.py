from typing import List, Optional

from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository


class TurmaService:
    def __init__(self) -> None:
        self._repo = TurmaRepository()

    def listar(self) -> List[Turma]:
        return Turma.listar()

    def buscar(self, id: int) -> Optional[Turma]:
        return Turma.buscar_por_id(id)

    def criar(self, dados: dict) -> Turma:
        if self._repo.buscar_id_por_codigo(dados["codigo"]):
            raise ValueError(f"Código de turma {dados['codigo']!r} já existe.")
        return Turma.criar(
            codigo=dados["codigo"], nome=dados["nome"],
            descricao=dados.get("descricao"), professor_id=dados["professor_id"]
        )

    def atualizar(self, id: int, dados: dict) -> Turma:
        turma = Turma.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")
        return turma.atualizar(**dados)

    def deletar(self, id: int) -> None:
        turma = Turma.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")
        turma.deletar()
