from database import db


class Conteudo(db.Model):
    __tablename__ = "conteudos"

    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey("turmas.id"))
    titulo = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    arquivo = db.Column(db.String(255))
    dataPostagem = db.Column(db.Date)
    turma = db.relationship("Turma")

    def to_dict(self):
        return {"id": self.id, "turma_id": self.turma_id, "titulo": self.titulo, "tipo": self.tipo, "arquivo": self.arquivo, "dataPostagem": self.dataPostagem.isoformat() if self.dataPostagem else None}
