from database import db


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def listar(self):
        return self.model.query.order_by(self.model.id).all()

    def buscar(self, identificador):
        return db.session.get(self.model, identificador)

    def criar(self, dados):
        try:
            registro = self.model(**dados)
            db.session.add(registro)
            db.session.commit()
            return registro
        except Exception:
            db.session.rollback()
            raise

    def atualizar(self, registro, dados):
        try:
            for campo, valor in dados.items():
                setattr(registro, campo, valor)
            db.session.commit()
            return registro
        except Exception:
            db.session.rollback()
            raise

    def excluir(self, registro):
        try:
            db.session.delete(registro)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
