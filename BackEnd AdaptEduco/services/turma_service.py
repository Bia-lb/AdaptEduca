from database import db
from models.turma import Turma


def listar():
    return Turma.query.all()


def buscar(id):
    return Turma.query.get(id)


def criar(codigo, nome, descricao, professor_id, responsavel_id):

    turma = Turma(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        professor_id=professor_id,
        responsavel_id=responsavel_id
    )

    db.session.add(turma)
    db.session.commit()


def atualizar(id, codigo, nome, descricao, professor_id, responsavel_id):

    turma = Turma.query.get(id)

    turma.codigo = codigo
    turma.nome = nome
    turma.descricao = descricao
    turma.professor_id = professor_id
    turma.responsavel_id = responsavel_id

    db.session.commit()


def excluir(id):

    turma = Turma.query.get(id)

    db.session.delete(turma)
    db.session.commit()