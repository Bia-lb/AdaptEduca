from app import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    tipoPerfil = db.Column(
        db.Enum("Aluno", "Professor", "Responsavel"),
        nullable=False
    )

    @classmethod
    def listar(cls):
        """Retorna todos os registros deste Model."""
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id):
        """Busca um registro pelo identificador."""
        return db.session.get(cls, id)

    @classmethod
    def criar(cls, dados):
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
        """Atualiza os campos permitidos deste Model."""
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

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipoPerfil": self.tipoPerfil
        }

    def __repr__(self):
        return f"<Usuario id={self.id} nome={self.nome}>"