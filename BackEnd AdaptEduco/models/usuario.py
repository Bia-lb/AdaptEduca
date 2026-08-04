from database import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipoPerfil = db.Column(db.String(30), nullable=False)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def atualizar(self):
        db.session.commit()

    def excluir(self):
        db.session.delete(self)
        db.session.commit()
        
    