from database import db

class Professor(db.Model):
    __tablename__ = "professores"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    formacao = db.Column(db.String(100))
    disciplina = db.Column(db.String(100))

    usuario = db.relationship("Usuario")