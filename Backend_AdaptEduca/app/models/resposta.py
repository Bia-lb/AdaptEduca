import json
from datetime import datetime

from app import db


class Resposta(db.Model):
    """Resposta de um aluno a uma atividade (RF15). Uma por aluno/atividade."""

    __tablename__ = "resposta"
    __table_args__ = (
        db.UniqueConstraint("atividade_id", "aluno_id", name="uq_resposta_atividade_aluno"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey("atividade.id"), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey("aluno.id"), nullable=False)
    respostas = db.Column(db.Text)  # JSON: lista de textos, na ordem das questões
    status = db.Column(
        db.Enum("Em andamento", "Enviada"), nullable=False, default="Em andamento"
    )
    etapasConcluidas = db.Column(db.Text)  # JSON: índices das etapas concluídas
    nota = db.Column(db.Float)             # 0 a 10, dada pelo professor
    atualizadaEm = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enviadaEm = db.Column(db.DateTime)

    def lista_respostas(self) -> list:
        try:
            dados = json.loads(self.respostas) if self.respostas else []
        except ValueError:
            return []
        return dados if isinstance(dados, list) else []

    def lista_etapas_concluidas(self) -> list:
        try:
            dados = json.loads(self.etapasConcluidas) if self.etapasConcluidas else []
        except ValueError:
            return []
        return dados if isinstance(dados, list) else []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atividade_id": self.atividade_id,
            "aluno_id": self.aluno_id,
            "respostas": self.lista_respostas(),
            "status": self.status,
            "etapasConcluidas": self.lista_etapas_concluidas(),
            "nota": self.nota,
            "enviadaEm": self.enviadaEm.isoformat() if self.enviadaEm else None,
        }
