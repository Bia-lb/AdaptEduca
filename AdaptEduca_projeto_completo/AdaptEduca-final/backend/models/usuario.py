from database import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    tipoPerfil = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "email": self.email, "tipoPerfil": self.tipoPerfil}
