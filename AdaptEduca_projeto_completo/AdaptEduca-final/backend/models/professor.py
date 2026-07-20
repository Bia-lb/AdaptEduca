from database import db


class Professor(db.Model):
    __tablename__ = "professores"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, unique=True)
    formacao = db.Column(db.String(100))
    disciplina = db.Column(db.String(100))
    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {"id": self.id, "usuario_id": self.usuario_id, "formacao": self.formacao, "disciplina": self.disciplina}
