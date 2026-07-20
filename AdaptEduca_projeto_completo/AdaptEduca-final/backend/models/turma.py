from database import db


class Turma(db.Model):
    __tablename__ = "turmas"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    professor_id = db.Column(db.Integer, db.ForeignKey("professores.id"))
    responsavel_id = db.Column(db.Integer, db.ForeignKey("responsaveis.id"))
    professor = db.relationship("Professor")
    responsavel = db.relationship("Responsavel")

    def to_dict(self):
        return {"id": self.id, "codigo": self.codigo, "nome": self.nome, "descricao": self.descricao, "professor_id": self.professor_id, "responsavel_id": self.responsavel_id}
