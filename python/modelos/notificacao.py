from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event

from python.banco import db


class TipoNotificacao(PyEnum):
    SugestaoLivro = 0
    ConviteChat = 1
    UsuarioSeguindo = 2


class Notificacao(db.Model):
    __tablename__ = 'notificacao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    titulo = db.Column(db.String(100), nullable=True, default="")
    conteudo = db.Column(db.String(1000), nullable=True, default="")
    img = db.Column(db.String(256), nullable=True, default="")
    tipo = db.Column(SAEnum(TipoNotificacao), nullable=False, default=TipoNotificacao.SugestaoLivro)
    lido = db.Column(db.Boolean, default=False)
    data_gravacao = db.Column(db.DateTime, default=datetime.now)

    def dicionario(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'img': self.img
        }
