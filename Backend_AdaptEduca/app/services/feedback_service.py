from datetime import date
from typing import List

from app import db
from app.models.aluno import Aluno
from app.models.atividade import Atividade
from app.models.feedback import Feedback
from app.models.resposta import Resposta

TIPOS = ("Incentivo", "Correcao", "Orientacao")


class FeedbackService:
    def criar(self, dados: dict, professor_id: int) -> Feedback:
        atividade = db.session.get(Atividade, dados.get("atividade_id") or 0)
        if not atividade or atividade.turma.professor_id != professor_id:
            raise PermissionError("Você só pode dar feedback em atividades das suas turmas.")
        aluno = db.session.get(Aluno, dados.get("aluno_id") or 0)
        if not aluno or atividade.turma not in aluno.turmas.all():
            raise LookupError("Aluno não faz parte da turma desta atividade.")
        tipo = dados.get("tipo") or "Orientacao"
        if tipo not in TIPOS:
            raise ValueError(f"Tipo inválido. Use: {', '.join(TIPOS)}.")
        mensagem = (dados.get("mensagem") or "").strip()
        if not mensagem:
            raise ValueError("Escreva a mensagem do feedback.")

        nota = dados.get("nota")
        if nota not in (None, ""):
            try:
                nota = float(nota)
            except (TypeError, ValueError):
                raise ValueError("Nota inválida.")
            if not 0 <= nota <= 10:
                raise ValueError("A nota deve estar entre 0 e 10.")
            resposta = Resposta.query.filter_by(atividade_id=atividade.id, aluno_id=aluno.id).first()
            if not resposta or resposta.status != "Enviada":
                raise ValueError("A nota só pode ser dada depois que o aluno enviar a atividade.")
            resposta.nota = nota
        fb = Feedback(mensagem=mensagem, tipo=tipo, data=date.today(),
                      atividade_id=atividade.id, aluno_id=aluno.id)
        db.session.add(fb)
        db.session.commit()
        return fb

    def listar_para(self, usuario_id: int, perfil: str, atividade_id=None, aluno_id=None) -> List[Feedback]:
        q = Feedback.query
        if atividade_id:
            q = q.filter(Feedback.atividade_id == atividade_id)
        if aluno_id:
            q = q.filter(Feedback.aluno_id == aluno_id)
        itens = q.order_by(Feedback.id.desc()).all()
        if perfil == "Professor":
            return [f for f in itens if f.atividade.turma.professor_id == usuario_id]
        if perfil == "Aluno":
            return [f for f in itens if f.aluno_id == usuario_id]
        if perfil == "Responsavel":
            from app.models.responsavel import Responsavel
            resp = Responsavel.buscar_por_id(usuario_id)
            ids = {a.id for a in resp.filhos} if resp else set()
            return [f for f in itens if f.aluno_id in ids]
        return []

    def deletar(self, id: int, professor_id: int) -> None:
        fb = db.session.get(Feedback, id)
        if not fb or fb.atividade.turma.professor_id != professor_id:
            raise LookupError("Feedback não encontrado.")
        db.session.delete(fb)
        db.session.commit()

    @staticmethod
    def dict_com_autor(fb: Feedback) -> dict:
        d = fb.to_dict()
        d["atividadeTitulo"] = fb.atividade.titulo
        d["professor"] = fb.atividade.turma.professor.nome
        return d
