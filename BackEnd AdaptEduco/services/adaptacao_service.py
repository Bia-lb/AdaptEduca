from database import db
from models.adaptacao import Adaptacao


def listar():
    return Adaptacao.query.all()


def buscar(id):
    return Adaptacao.query.get(id)


def criar(conteudo_id, modo, resumo, audio, mapaMental):

    adaptacao = Adaptacao(
        conteudo_id=conteudo_id,
        modo=modo,
        resumo=resumo,
        audio=audio,
        mapaMental=mapaMental
    )

    db.session.add(adaptacao)
    db.session.commit()


def atualizar(id, conteudo_id, modo, resumo, audio, mapaMental):

    adaptacao = Adaptacao.query.get(id)

    adaptacao.conteudo_id = conteudo_id
    adaptacao.modo = modo
    adaptacao.resumo = resumo
    adaptacao.audio = audio
    adaptacao.mapaMental = mapaMental

    db.session.commit()


def excluir(id):

    adaptacao = Adaptacao.query.get(id)

    db.session.delete(adaptacao)
    db.session.commit()