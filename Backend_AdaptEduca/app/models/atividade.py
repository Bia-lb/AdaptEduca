from app import db


class Atividade(db.Model):
    __tablename__ = "atividade"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text)
    prazo = db.Column(db.Date)
    status = db.Column(
        db.Enum("Pendente", "Concluida"),
        nullable=False,
        default="Pendente",
    )
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)

    feedbacks = db.relationship("Feedback", backref="atividade", lazy=True)


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
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prazo": self.prazo.isoformat() if self.prazo else None,
            "status": self.status,
            "turma_id": self.turma_id,
        }

    def __repr__(self) -> str:
        return f"<Atividade id={self.id} titulo={self.titulo!r}>"
