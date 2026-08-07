from typing import List, Optional
from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository


class TurmaService:
    def __init__(self) -> None:
        self._repo = TurmaRepository()

    def listar(self) -> List[Turma]:
        return self._repo.listar_todos()

    def buscar(self, id: int) -> Optional[Turma]:
        return self._repo.buscar_por_id(id)

    def criar(self, dados: dict) -> Turma:
        if self._repo.buscar_por_codigo(dados["codigo"]):
            raise ValueError(f"Código de turma {dados['codigo']!r} já existe.")

        turma = Turma(
            codigo=dados["codigo"],
            nome=dados["nome"],
            descricao=dados.get("descricao"),
            professor_id=dados["professor_id"],
        )
        return self._repo.salvar(turma)

    def atualizar(self, id: int, dados: dict) -> Turma:
        turma = self._repo.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")

        turma.nome = dados.get("nome", turma.nome)
        turma.descricao = dados.get("descricao", turma.descricao)
        turma.professor_id = dados.get("professor_id", turma.professor_id)
        return self._repo.salvar(turma)

    def deletar(self, id: int) -> None:
        turma = self._repo.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")
        self._repo.deletar(turma)
