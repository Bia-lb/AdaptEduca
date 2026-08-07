from app import db

# Tabela associativa Aluno <-> Turma
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
