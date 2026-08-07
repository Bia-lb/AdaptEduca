from app import db


class Adaptacao(db.Model):
    """Stub — CRUD completo a implementar na próxima iteração."""
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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "modo": self.modo,
            "resumo": self.resumo,
            "audio": self.audio,
            "mapaMental": self.mapaMental,
            "conteudo_id": self.conteudo_id,
        }
