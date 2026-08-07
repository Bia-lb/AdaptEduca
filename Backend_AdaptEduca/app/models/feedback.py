from app import db


class Feedback(db.Model):
    """Stub — CRUD completo a implementar na próxima iteração."""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mensagem = db.Column(db.Text, nullable=False)
    data = db.Column(db.Date)
    tipo = db.Column(
        db.Enum("Incentivo", "Correcao", "Orientacao"),
        nullable=False,
    )
    atividade_id = db.Column(
        db.Integer, db.ForeignKey("atividade.id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mensagem": self.mensagem,
            "data": self.data.isoformat() if self.data else None,
            "tipo": self.tipo,
            "atividade_id": self.atividade_id,
        }
