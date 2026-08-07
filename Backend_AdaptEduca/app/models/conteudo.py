from app import db


class Conteudo(db.Model):
    __tablename__ = "conteudo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.Enum("Texto", "PDF", "Video", "Link"), nullable=False)
    arquivo = db.Column(db.String(255))
    dataPostagem = db.Column(db.Date)
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)

    adaptacoes = db.relationship("Adaptacao", backref="conteudo", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "arquivo": self.arquivo,
            "dataPostagem": (
                self.dataPostagem.isoformat() if self.dataPostagem else None
            ),
            "turma_id": self.turma_id,
        }

    def __repr__(self) -> str:
        return f"<Conteudo id={self.id} titulo={self.titulo!r}>"
