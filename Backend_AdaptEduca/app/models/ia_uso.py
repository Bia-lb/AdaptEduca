from datetime import date

from app import db


class IAUso(db.Model):
    """Contador diário de chamadas à IA por usuário (controle de custo/abuso)."""
    __tablename__ = "ia_uso"
    __table_args__ = (db.UniqueConstraint("usuario_id", "dia", name="uq_ia_uso_usuario_dia"),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    dia = db.Column(db.Date, nullable=False, default=date.today)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
