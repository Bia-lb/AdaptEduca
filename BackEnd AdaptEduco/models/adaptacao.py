from database import db

class Adaptacao(db.Model):
    __tablename__ = "adaptacoes"

    id = db.Column(db.Integer, primary_key=True)

    conteudo_id = db.Column(
        db.Integer,
        db.ForeignKey("conteudos.id")
    )

    modo = db.Column(db.String(100))
    resumo = db.Column(db.String(255))
    audio = db.Column(db.Boolean)
    mapaMental = db.Column(db.Boolean)

    conteudo = db.relationship("Conteudo")