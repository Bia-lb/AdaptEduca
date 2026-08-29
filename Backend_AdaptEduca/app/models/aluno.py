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
