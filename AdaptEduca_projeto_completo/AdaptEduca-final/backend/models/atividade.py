from database import db


class Atividade(db.Model):
    __tablename__ = "atividades"

    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey("turmas.id"))
    conteudo_id = db.Column(db.Integer, db.ForeignKey("conteudos.id"))
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    prazo = db.Column(db.Date)
    status = db.Column(db.String(30))
    turma = db.relationship("Turma")
    conteudo = db.relationship("Conteudo")

    def to_dict(self):
        return {"id": self.id, "turma_id": self.turma_id, "conteudo_id": self.conteudo_id, "titulo": self.titulo, "descricao": self.descricao, "prazo": self.prazo.isoformat() if self.prazo else None, "status": self.status}
