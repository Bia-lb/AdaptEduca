from database import db
from models.relatorio import Relatorio


def listar():
    return Relatorio.query.all()


def buscar(id):
    return Relatorio.query.get(id)


def criar(aluno_id, desempenho, tempoEstudo, materiasDificeis, periodo):

    relatorio = Relatorio(
        aluno_id=aluno_id,
        desempenho=desempenho,
        tempoEstudo=tempoEstudo,
        materiasDificeis=materiasDificeis,
        periodo=periodo
    )

    db.session.add(relatorio)
    db.session.commit()


def atualizar(id, aluno_id, desempenho, tempoEstudo, materiasDificeis, periodo):

    relatorio = Relatorio.query.get(id)

    relatorio.aluno_id = aluno_id
    relatorio.desempenho = desempenho
    relatorio.tempoEstudo = tempoEstudo
    relatorio.materiasDificeis = materiasDificeis
    relatorio.periodo = periodo

    db.session.commit()


def excluir(id):

    relatorio = Relatorio.query.get(id)

    db.session.delete(relatorio)
    db.session.commit()