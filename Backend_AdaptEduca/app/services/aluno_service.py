import json
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

    CAMPOS_EDITAVEIS = ("nome", "email", "senha", "dataNascimento", "preferenciaAprendizagem")

    def atualizar(self, id: int, dados: dict) -> Aluno:
        aluno = Aluno.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        campos = {k: v for k, v in dados.items() if k in self.CAMPOS_EDITAVEIS}
        if "dataNascimento" in campos:
            campos["dataNascimento"] = date.fromisoformat(campos["dataNascimento"]) if campos["dataNascimento"] else None
        return aluno.atualizar(**campos)

    def salvar_questionario(self, id: int, respostas: dict) -> Aluno:
        """RF04: grava o questionário completo e resume os formatos preferidos."""
        aluno = Aluno.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        if not isinstance(respostas, dict) or not respostas:
            raise ValueError("Envie as respostas do questionário.")
        formatos = respostas.get("formats")
        if not isinstance(formatos, list) or not formatos:
            raise ValueError("Selecione ao menos um formato de aprendizagem.")
        resumo = ", ".join(str(f) for f in formatos)[:80]
        return aluno.atualizar(
            questionario=json.dumps(respostas, ensure_ascii=False),
            questionarioConcluido=True,
            preferenciaAprendizagem=resumo,
        )

    def deletar(self, id: int) -> None:
        aluno = Aluno.buscar_por_id(id)
        if not aluno:
            raise LookupError(f"Aluno {id} não encontrado.")
        aluno.deletar()
