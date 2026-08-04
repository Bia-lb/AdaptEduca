from database import db
from models.responsavel import Responsavel


def listar():
    return Responsavel.query.all()


def buscar(id):
    return Responsavel.query.get(id)


def criar(usuario_id, parentesco, telefone):

    responsavel = Responsavel(
        usuario_id=usuario_id,
        parentesco=parentesco,
        telefone=telefone
    )

    db.session.add(responsavel)
    db.session.commit()


def atualizar(id, usuario_id, parentesco, telefone):

    responsavel = Responsavel.query.get(id)

    responsavel.usuario_id = usuario_id
    responsavel.parentesco = parentesco
    responsavel.telefone = telefone

    db.session.commit()


def excluir(id):

    responsavel = Responsavel.query.get(id)

    db.session.delete(responsavel)
    db.session.commit()