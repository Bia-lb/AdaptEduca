from app import db


class Atividade(db.Model):
    __tablename__ = "atividade"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text)
    prazo = db.Column(db.Date)
    status = db.Column(
        db.Enum("Pendente", "Concluida"),
        nullable=False,
        default="Pendente",
    )
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)

    feedbacks = db.relationship("Feedback", backref="atividade", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prazo": self.prazo.isoformat() if self.prazo else None,
            "status": self.status,
            "turma_id": self.turma_id,
        }

    def __repr__(self) -> str:
        return f"<Atividade id={self.id} titulo={self.titulo!r}>"
