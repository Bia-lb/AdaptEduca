from database import db

class Responsavel(db.Model):
    __tablename__ = "responsaveis"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    parentesco = db.Column(db.String(50))
    telefone = db.Column(db.String(20))

    usuario = db.relationship("Usuario")