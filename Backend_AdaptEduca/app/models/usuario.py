from app import db


class Usuario(db.Model):
    """
    Entidade raiz do diagrama UML.
    Decisão técnica: herança de tabela única (Single Table Inheritance)
    usando a coluna tipoPerfil como discriminador, mantendo o padrão UML.
    """
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    tipoPerfil = db.Column(
        db.Enum("Aluno", "Professor", "Responsavel"),
        nullable=False,
    )

    __mapper_args__ = {
        "polymorphic_on": tipoPerfil,
        "polymorphic_identity": "Usuario",
    }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipoPerfil": self.tipoPerfil,
        }

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} nome={self.nome!r}>"
