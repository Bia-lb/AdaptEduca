from app import db
from .usuario import Usuario

# Tabela associativa Responsavel <-> Turma (observação de turma pelo responsável)
responsavel_turma = db.Table(
    "responsavel_turma",
    db.Column("responsavel_id", db.Integer, db.ForeignKey("responsavel.id"), primary_key=True),
    db.Column("turma_id", db.Integer, db.ForeignKey("turma.id"), primary_key=True),
)


class Responsavel(Usuario):
    __tablename__ = "responsavel"

    id = db.Column(db.Integer, db.ForeignKey("usuario.id"), primary_key=True)
    parentesco = db.Column(db.String(40))
    telefone = db.Column(db.String(20))

    turmas = db.relationship(
        "Turma",
        secondary=responsavel_turma,
        backref=db.backref("responsaveis", lazy="dynamic"),
        lazy=True,
    )

    __mapper_args__ = {"polymorphic_identity": "Responsavel"}

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "parentesco": self.parentesco,
            "telefone": self.telefone,
        })
        return base

    def __repr__(self) -> str:
        return f"<Responsavel id={self.id} parentesco={self.parentesco!r}>"
