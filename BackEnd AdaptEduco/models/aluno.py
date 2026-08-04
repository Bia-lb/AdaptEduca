from database import db

class Aluno(db.Model):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    matricula = db.Column(db.String(20), nullable=False)
    preferenciaAprendizagem = db.Column(db.String(100))
    progresso = db.Column(db.Float)
    dataNascimento = db.Column(db.Date)

    usuario = db.relationship("Usuario")