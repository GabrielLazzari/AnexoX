from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event

from python.banco import db


class OrigemReacao(PyEnum):
    Livro = 0
    Comentario = 1
    Publicacao = 2


class ReacaoTipo(db.Model):
    __tablename__ = 'reacao_tipo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="")
    descricao = db.Column(db.String(500), nullable=True, default="")
    icone = db.Column(db.String(256), nullable=True, default="")


class Reacao(db.Model):
    __tablename__ = 'reacao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    reacao_id = db.Column(db.Integer, db.ForeignKey('reacao_tipo.id'))
    reacao = db.relationship('ReacaoTipo', foreign_keys=[reacao_id])
    origem = db.Column(SAEnum(OrigemReacao), nullable=False, default=OrigemReacao.Livro)
    origem_id = db.Column(db.Integer)
    data_gravacao = db.Column(db.DateTime, default=datetime.now)

    def dicionario(self):
        return {
            'id': self.id,
            'reacao_nome': self.reacao.nome,
            'reacao_icone': self.reacao.icone,
            'usuario_id': self.usuario_id
        }


@event.listens_for(ReacaoTipo.__table__, 'after_create')
def inserir_tipos_reacoes_estaticos(target, connection, **kw):
    connection.execute(
        ReacaoTipo.__table__.insert(),
        [
            {"nome": "Muito bom", "descricao": "", "icone": "😍"},
            {"nome": "Bom", "descricao": "", "icone": "😊"},
            {"nome": "Ok", "descricao": "", "icone": "😐"},
            {"nome": "Ruim", "descricao": "", "icone": "😕"},
            {"nome": "Muito Ruim", "descricao": "", "icone": "😠"},
            {"nome": "Não gostei", "descricao": "", "icone": "😡"},
            {"nome": "Coração", "descricao": "", "icone": "❤️"},
        ]
    )
