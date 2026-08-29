from datetime import date
from typing import List, Optional

from app.models.aluno import Aluno
from app.repositories.aluno_repository import AlunoRepository


class AlunoService:
    def __init__(self) -> None:
        self._repo = AlunoRepository()

    def listar(self) -> List[Aluno]:
        return Aluno.listar()

    def buscar(self, id: int) -> Optional[Aluno]:
        return Aluno.buscar_por_id(id)

    def criar(self, dados: dict) -> Aluno:
        if self._repo.buscar_id_por_matricula(dados["matricula"]):
            raise ValueError(f"Matrícula {dados['matricula']!r} já existe.")
        nascimento = date.fromisoformat(dados["dataNascimento"]) if dados.get("dataNascimento") else None
        return Aluno.criar(
            nome=dados["nome"], email=dados["email"], senha=dados["senha"],
            tipoPerfil="Aluno", matricula=dados["matricula"],
            preferenciaAprendizagem=dados.get("preferenciaAprendizagem"),
            progresso=dados.get("progresso", 0.0), dataNascimento=nascimento,
        )

    def atualizar(self, id: int, dados: dict) -> Aluno:
        aluno = Aluno.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        if "dataNascimento" in dados:
            dados["dataNascimento"] = date.fromisoformat(dados["dataNascimento"]) if dados["dataNascimento"] else None
        return aluno.atualizar(**dados)

    def deletar(self, id: int) -> None:
        aluno = Aluno.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        aluno.deletar()
