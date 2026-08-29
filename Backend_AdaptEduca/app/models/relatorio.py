from app import db


class Relatorio(db.Model):
    __tablename__ = "relatorio"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desempenho = db.Column(db.Float)
    tempoEstudo = db.Column(db.Float)
    materiasDificeis = db.Column(db.String(255))
    periodo = db.Column(db.String(40))
    aluno_id = db.Column(db.Integer, db.ForeignKey("aluno.id"), nullable=False)


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
            "desempenho": self.desempenho,
            "tempoEstudo": self.tempoEstudo,
            "materiasDificeis": self.materiasDificeis,
            "periodo": self.periodo,
            "aluno_id": self.aluno_id,
        }
