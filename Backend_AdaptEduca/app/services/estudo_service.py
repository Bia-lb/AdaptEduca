from typing import Optional

from app import db
from app.models.aluno import Aluno
from app.models.sessao_estudo import SessaoEstudo
from app.services import adaptacao_engine as motor

MODOS_VALIDOS = ("leitura", "foco", "revisao", "audio")
MAX_SEGUNDOS = 4 * 60 * 60


class EstudoService:
    def modos(self, aluno: Aluno) -> dict:
        return motor.modos_de_estudo(aluno.respostas_questionario())

    def registrar(self, aluno: Aluno, modo: str, segundos, conteudo_id: Optional[int] = None) -> SessaoEstudo:
        if modo not in MODOS_VALIDOS:
            raise ValueError(f"Modo inválido. Use: {', '.join(MODOS_VALIDOS)}.")
        try:
            segundos = int(segundos)
        except (TypeError, ValueError):
            raise ValueError("Duração inválida.")
        if not 5 <= segundos <= MAX_SEGUNDOS:
            raise ValueError("Duração fora do intervalo permitido (5 s a 4 h).")
        if conteudo_id is not None:
            from app.models.conteudo import Conteudo
            c = db.session.get(Conteudo, conteudo_id)
            if not c or c.turma not in aluno.turmas.all():
                raise PermissionError("Conteúdo não encontrado.")
        sessao = SessaoEstudo(aluno_id=aluno.id, modo=modo, segundos=segundos, conteudo_id=conteudo_id)
        db.session.add(sessao)
        db.session.commit()
        return sessao
