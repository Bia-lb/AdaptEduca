from app import db


class Adaptacao(db.Model):
    __tablename__ = "adaptacao"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modo = db.Column(
        db.Enum("Texto simplificado", "Audio", "Video", "Mapa mental", "Resumo"),
        nullable=False,
    )
    resumo = db.Column(db.Text)
    audio = db.Column(db.Boolean, default=False)
    mapaMental = db.Column(db.Boolean, default=False)
    conteudo_id = db.Column(db.Integer, db.ForeignKey("conteudo.id"), nullable=False)


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
            "modo": self.modo,
            "resumo": self.resumo,
            "audio": self.audio,
            "mapaMental": self.mapaMental,
            "conteudo_id": self.conteudo_id,
        }
