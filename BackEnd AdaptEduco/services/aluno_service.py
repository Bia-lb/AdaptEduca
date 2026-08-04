from database import db
from models.aluno import Aluno


def listar():
    return Aluno.query.all()


def buscar(id):
    return Aluno.query.get(id)


def criar(usuario_id, matricula, preferenciaAprendizagem, progresso, dataNascimento):

    aluno = Aluno(
        usuario_id=usuario_id,
        matricula=matricula,
        preferenciaAprendizagem=preferenciaAprendizagem,
        progresso=progresso,
        dataNascimento=dataNascimento
    )

    db.session.add(aluno)
    db.session.commit()


def atualizar(id, usuario_id, matricula, preferenciaAprendizagem, progresso, dataNascimento):

    aluno = Aluno.query.get(id)

    aluno.usuario_id = usuario_id
    aluno.matricula = matricula
    aluno.preferenciaAprendizagem = preferenciaAprendizagem
    aluno.progresso = progresso
    aluno.dataNascimento = dataNascimento

    db.session.commit()


def excluir(id):

    aluno = Aluno.query.get(id)

    db.session.delete(aluno)
    db.session.commit()