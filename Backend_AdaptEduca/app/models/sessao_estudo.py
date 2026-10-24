from datetime import datetime, timezone

from app import db


def _agora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SessaoEstudo(db.Model):
    """Registro de uma sessão de estudo do aluno (RF14/RF16)."""

    __tablename__ = "sessao_estudo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey("aluno.id"), nullable=False)
    conteudo_id = db.Column(db.Integer, db.ForeignKey("conteudo.id"), nullable=True)
    modo = db.Column(db.String(30), nullable=False)
    segundos = db.Column(db.Integer, nullable=False)
    iniciadaEm = db.Column(db.DateTime, nullable=False, default=_agora)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "aluno_id": self.aluno_id, "conteudo_id": self.conteudo_id,
            "modo": self.modo, "segundos": self.segundos,
            "iniciadaEm": self.iniciadaEm.isoformat(),
        }
