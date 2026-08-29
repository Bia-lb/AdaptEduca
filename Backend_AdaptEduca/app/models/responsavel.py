from app import db
from .usuario import Usuario


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


    @classmethod
    def listar(cls):
        """Retorna todos os registros desta Model."""
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id):
        """Busca um registro pelo identificador."""
        return db.session.get(cls, id)

    @classmethod
    def criar(cls, **dados):
        """Cria, persiste e retorna um novo registro."""
        entidade = cls(**dados)
        try:
            db.session.add(entidade)
            db.session.commit()
            return entidade
        except Exception:
            db.session.rollback()
            raise

    def atualizar(self, **dados):
        """Atualiza os campos permitidos desta Model."""
        for campo, valor in dados.items():
            if hasattr(self, campo) and campo != "id":
                setattr(self, campo, valor)
        try:
            db.session.commit()
            return self
        except Exception:
            db.session.rollback()
            raise

    def deletar(self):
        """Remove este registro do banco."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "parentesco": self.parentesco,
            "telefone": self.telefone,
        })
        return base

    def __repr__(self) -> str:
        return f"<Responsavel id={self.id} parentesco={self.parentesco!r}>"
