from app import db
from .usuario import Usuario


class Professor(Usuario):
    __tablename__ = "professor"

    id = db.Column(db.Integer, db.ForeignKey("usuario.id"), primary_key=True)
    formacao = db.Column(db.String(120))
    disciplina = db.Column(db.String(80))

    turmas = db.relationship("Turma", backref="professor", lazy=True)

    __mapper_args__ = {"polymorphic_identity": "Professor"}


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
            "formacao": self.formacao,
            "disciplina": self.disciplina,
        })
        return base

    def __repr__(self) -> str:
        return f"<Professor id={self.id} disciplina={self.disciplina!r}>"
