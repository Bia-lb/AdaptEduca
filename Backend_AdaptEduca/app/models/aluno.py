from app import db
from .usuario import Usuario


class Aluno(Usuario):
    __tablename__ = "aluno"

    id = db.Column(db.Integer, db.ForeignKey("usuario.id"), primary_key=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    preferenciaAprendizagem = db.Column(db.String(80))
    progresso = db.Column(db.Float, default=0.0)
    dataNascimento = db.Column(db.Date)

    relatorios = db.relationship("Relatorio", backref="aluno", lazy=True)

    __mapper_args__ = {"polymorphic_identity": "Aluno"}

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "matricula": self.matricula,
            "preferenciaAprendizagem": self.preferenciaAprendizagem,
            "progresso": self.progresso,
            "dataNascimento": (
                self.dataNascimento.isoformat() if self.dataNascimento else None
            ),
        })
        return base

    def __repr__(self) -> str:
        return f"<Aluno id={self.id} matricula={self.matricula!r}>"
