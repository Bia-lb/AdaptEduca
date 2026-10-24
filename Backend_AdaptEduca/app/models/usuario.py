import hmac

from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

_PREFIXOS_HASH = ("pbkdf2:", "scrypt:")


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

    # Permite que Usuario.query devolva Aluno/Professor/Responsavel já tipados
    # (sem isso, o identity map devolve a instância genérica Usuario).
    __mapper_args__ = {"polymorphic_on": tipoPerfil}

    @validates("senha")
    def _hash_senha(self, _chave, valor):
        """Garante que a senha seja sempre gravada como hash."""
        if valor and not valor.startswith(_PREFIXOS_HASH):
            return generate_password_hash(valor, method="pbkdf2:sha256")
        return valor

    def verificar_senha(self, senha: str) -> bool:
        """Confere a senha. Senhas legadas em texto puro são migradas para hash."""
        if self.senha.startswith(_PREFIXOS_HASH):
            return check_password_hash(self.senha, senha)
        if hmac.compare_digest(self.senha.encode(), senha.encode()):
            self.senha = senha  # o validator converte em hash
            db.session.commit()
            return True
        return False

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