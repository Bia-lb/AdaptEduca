from app import db


aluno_turma = db.Table(
    "aluno_turma",
    db.Column("aluno_id", db.Integer, db.ForeignKey("aluno.id"), primary_key=True),
    db.Column("turma_id", db.Integer, db.ForeignKey("turma.id"), primary_key=True),
)


class Turma(db.Model):
    __tablename__ = "turma"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text)

    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)

    alunos = db.relationship(
        "Aluno",
        secondary=aluno_turma,
        backref=db.backref("turmas", lazy="dynamic"),
        lazy=True,
    )

    conteudos = db.relationship("Conteudo", backref="turma", lazy=True)
    atividades = db.relationship("Atividade", backref="turma", lazy=True)


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
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "professor_id": self.professor_id,
        }

    def __repr__(self) -> str:
        return f"<Turma id={self.id} codigo={self.codigo!r}>"
