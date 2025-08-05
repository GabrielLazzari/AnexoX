from datetime import datetime

from python.banco import db

class Publicacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=True, default="")
    data_gravacao = db.Column(db.DateTime, default=datetime.now())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'data': self.data_gravacao.strftime('%d/%m/%Y') if self.data_gravacao else None,
            'hora': self.data_gravacao.strftime('%H:%M') if self.data_gravacao else None,
            'idUsuario': self.usuario.id,
            'nomeUsuario': self.usuario.nome,
            'imgUsuario': self.usuario.img
        }

    def validar_campos(self):
        msg_erro = ""

        self.titulo = self.titulo.strip()

        return msg_erro
