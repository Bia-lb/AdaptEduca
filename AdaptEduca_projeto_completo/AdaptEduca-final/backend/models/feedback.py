from database import db


class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey("atividades.id"))
    mensagem = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    atividade = db.relationship("Atividade")

    def to_dict(self):
        return {"id": self.id, "atividade_id": self.atividade_id, "mensagem": self.mensagem, "data": self.data.isoformat() if self.data else None, "tipo": self.tipo}
