from app import db


class Relatorio(db.Model):
    """Stub — CRUD completo a implementar na próxima iteração."""
    __tablename__ = "relatorio"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desempenho = db.Column(db.Float)
    tempoEstudo = db.Column(db.Float)
    materiasDificeis = db.Column(db.String(255))
    periodo = db.Column(db.String(40))
    aluno_id = db.Column(db.Integer, db.ForeignKey("aluno.id"), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "desempenho": self.desempenho,
            "tempoEstudo": self.tempoEstudo,
            "materiasDificeis": self.materiasDificeis,
            "periodo": self.periodo,
            "aluno_id": self.aluno_id,
        }
