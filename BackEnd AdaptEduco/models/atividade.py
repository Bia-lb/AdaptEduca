from database import db

class Atividade(db.Model):
    __tablename__ = "atividades"

    id = db.Column(db.Integer, primary_key=True)

    turma_id = db.Column(
        db.Integer,
        db.ForeignKey("turmas.id")
    )

    conteudo_id = db.Column(
        db.Integer,
        db.ForeignKey("conteudos.id")
    )

    titulo = db.Column(db.String(100))
    descricao = db.Column(db.String(255))
    prazo = db.Column(db.Date)
    status = db.Column(db.String(30))

    turma = db.relationship("Turma")
    conteudo = db.relationship("Conteudo")