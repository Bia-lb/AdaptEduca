from database import db


class Aluno(db.Model):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, unique=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    preferenciaAprendizagem = db.Column(db.String(100))
    progresso = db.Column(db.Float, default=0)
    dataNascimento = db.Column(db.Date)
    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {"id": self.id, "usuario_id": self.usuario_id, "matricula": self.matricula, "preferenciaAprendizagem": self.preferenciaAprendizagem, "progresso": self.progresso, "dataNascimento": self.dataNascimento.isoformat() if self.dataNascimento else None}
