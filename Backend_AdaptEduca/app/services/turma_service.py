from typing import List, Optional

from app import db
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.responsavel import Responsavel
from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository

CAMPOS_EDITAVEIS = ("nome", "descricao")


class TurmaService:
    def __init__(self) -> None:
        self._repo = TurmaRepository()

    def listar(self) -> List[Turma]:
        return Turma.listar()

    def listar_para(self, usuario_id: int, perfil: str) -> List[Turma]:
        """Cada perfil enxerga apenas as turmas com as quais tem vínculo."""
        if perfil == "Professor":
            return Turma.query.filter_by(professor_id=usuario_id).order_by(Turma.nome).all()
        if perfil == "Aluno":
            aluno = Aluno.buscar_por_id(usuario_id)
            return sorted(aluno.turmas.all(), key=lambda t: t.nome) if aluno else []
        if perfil == "Responsavel":
            resp = Responsavel.buscar_por_id(usuario_id)
            return sorted(resp.turmas, key=lambda t: t.nome) if resp else []
        return []

    def buscar(self, id: int) -> Optional[Turma]:
        return Turma.buscar_por_id(id)

    def tem_acesso(self, turma: Turma, usuario_id: int, perfil: str) -> bool:
        return any(t.id == turma.id for t in self.listar_para(usuario_id, perfil))

    def criar(self, dados: dict, professor_id: int) -> Turma:
        if not Professor.buscar_por_id(professor_id):
            raise ValueError("Apenas professores podem criar turmas.")
        codigo = str(dados["codigo"]).strip()
        nome = str(dados["nome"]).strip()
        if not codigo or not nome:
            raise ValueError("Código e nome da turma são obrigatórios.")
        if self._repo.buscar_id_por_codigo(codigo):
            raise ValueError(f"Código de turma {codigo!r} já existe.")
        return Turma.criar(
            codigo=codigo, nome=nome,
            descricao=dados.get("descricao"), professor_id=professor_id,
        )

    def atualizar(self, id: int, dados: dict) -> Turma:
        turma = Turma.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")
        return turma.atualizar(**{k: v for k, v in dados.items() if k in CAMPOS_EDITAVEIS})

    def deletar(self, id: int) -> None:
        turma = Turma.buscar_por_id(id)
        if not turma:
            raise LookupError(f"Turma {id} não encontrada.")
        turma.deletar()

    # ── vínculo aluno ↔ turma (RF05) ────────────────────────────────────────
    def adicionar_aluno(self, turma: Turma, dados: dict) -> Aluno:
        aluno = self._localizar_aluno(dados)
        if aluno is None:
            raise LookupError("Aluno não encontrado. Confira a matrícula ou o e-mail.")
        if aluno in turma.alunos:
            raise ValueError("Este aluno já faz parte da turma.")
        turma.alunos.append(aluno)
        db.session.commit()
        return aluno

    def remover_aluno(self, turma: Turma, aluno_id: int) -> None:
        aluno = Aluno.buscar_por_id(aluno_id)
        if aluno is None or aluno not in turma.alunos:
            raise LookupError("Aluno não faz parte desta turma.")
        turma.alunos.remove(aluno)
        db.session.commit()

    @staticmethod
    def _localizar_aluno(dados: dict) -> Optional[Aluno]:
        if dados.get("aluno_id"):
            return Aluno.buscar_por_id(int(dados["aluno_id"]))
        if dados.get("matricula"):
            return Aluno.query.filter_by(matricula=str(dados["matricula"]).strip()).first()
        if dados.get("email"):
            return Aluno.query.filter(
                db.func.lower(Aluno.email) == str(dados["email"]).strip().lower()
            ).first()
        return None
