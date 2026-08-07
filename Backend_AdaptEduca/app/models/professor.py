from app import db
from .usuario import Usuario


class Professor(Usuario):
    __tablename__ = "professor"

    id = db.Column(db.Integer, db.ForeignKey("usuario.id"), primary_key=True)
    formacao = db.Column(db.String(120))
    disciplina = db.Column(db.String(80))

    turmas = db.relationship("Turma", backref="professor", lazy=True)

    __mapper_args__ = {"polymorphic_identity": "Professor"}

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "formacao": self.formacao,
            "disciplina": self.disciplina,
        })
        return base

    def __repr__(self) -> str:
        return f"<Professor id={self.id} disciplina={self.disciplina!r}>"
