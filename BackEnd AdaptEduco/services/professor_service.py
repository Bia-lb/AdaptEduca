from database import db
from models.professor import Professor


def listar():
    return Professor.query.all()


def buscar(id):
    return Professor.query.get(id)


def criar(usuario_id, formacao, disciplina):

    professor = Professor(
        usuario_id=usuario_id,
        formacao=formacao,
        disciplina=disciplina
    )

    db.session.add(professor)
    db.session.commit()


def atualizar(id, usuario_id, formacao, disciplina):

    professor = Professor.query.get(id)

    professor.usuario_id = usuario_id
    professor.formacao = formacao
    professor.disciplina = disciplina

    db.session.commit()


def excluir(id):

    professor = Professor.query.get(id)

    db.session.delete(professor)
    db.session.commit()