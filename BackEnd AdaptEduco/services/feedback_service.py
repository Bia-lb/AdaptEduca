from database import db
from models.atividade import Atividade


def listar():
    return Atividade.query.all()


def buscar(id):
    return Atividade.query.get(id)


def criar(turma_id, conteudo_id, titulo, descricao, prazo, status):

    atividade = Atividade(
        turma_id=turma_id,
        conteudo_id=conteudo_id,
        titulo=titulo,
        descricao=descricao,
        prazo=prazo,
        status=status
    )

    db.session.add(atividade)
    db.session.commit()


def atualizar(id, turma_id, conteudo_id, titulo, descricao, prazo, status):

    atividade = Atividade.query.get(id)

    atividade.turma_id = turma_id
    atividade.conteudo_id = conteudo_id
    atividade.titulo = titulo
    atividade.descricao = descricao
    atividade.prazo = prazo
    atividade.status = status

    db.session.commit()


def excluir(id):

    atividade = Atividade.query.get(id)

    db.session.delete(atividade)
    db.session.commit()