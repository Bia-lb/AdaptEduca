from database import db

class Relatorio(db.Model):
    __tablename__ = "relatorios"

    id = db.Column(db.Integer, primary_key=True)

    aluno_id = db.Column(
        db.Integer,
        db.ForeignKey("alunos.id")
    )

    desempenho = db.Column(db.Float)
    tempoEstudo = db.Column(db.Float)
    materiasDificeis = db.Column(db.String(255))
    periodo = db.Column(db.String(50))

    aluno = db.relationship("Aluno")