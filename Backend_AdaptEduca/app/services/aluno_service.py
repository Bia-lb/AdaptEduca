from datetime import date
from typing import List, Optional
from app.models.aluno import Aluno
from app.repositories.aluno_repository import AlunoRepository


class AlunoService:
    def __init__(self) -> None:
        self._repo = AlunoRepository()

    def listar(self) -> List[Aluno]:
        return self._repo.listar_todos()

    def buscar(self, id: int) -> Optional[Aluno]:
        return self._repo.buscar_por_id(id)

    def criar(self, dados: dict) -> Aluno:
        if self._repo.buscar_por_matricula(dados["matricula"]):
            raise ValueError(f"Matrícula {dados['matricula']!r} já existe.")

        nascimento = None
        if dados.get("dataNascimento"):
            nascimento = date.fromisoformat(dados["dataNascimento"])

        aluno = Aluno(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            tipoPerfil="Aluno",
            matricula=dados["matricula"],
            preferenciaAprendizagem=dados.get("preferenciaAprendizagem"),
            progresso=dados.get("progresso", 0.0),
            dataNascimento=nascimento,
        )
        return self._repo.salvar(aluno)

    def atualizar(self, id: int, dados: dict) -> Aluno:
        aluno = self._repo.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")

        aluno.nome = dados.get("nome", aluno.nome)
        aluno.email = dados.get("email", aluno.email)
        aluno.preferenciaAprendizagem = dados.get(
            "preferenciaAprendizagem", aluno.preferenciaAprendizagem
        )
        aluno.progresso = dados.get("progresso", aluno.progresso)
        if dados.get("dataNascimento"):
            aluno.dataNascimento = date.fromisoformat(dados["dataNascimento"])

        return self._repo.salvar(aluno)

    def deletar(self, id: int) -> None:
        aluno = self._repo.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        self._repo.deletar(aluno)
