from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event

from python.banco import db
from python.modelos.reacao import *


class OrigemComentario(PyEnum):
    Livro = 0
    Comentario = 1
    Publicacao = 2


class Comentario(db.Model):
    __tablename__ = 'comentario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    conteudo = db.Column(db.String(2000), nullable=False, default="")
    reacoes = db.relationship('Reacao', primaryjoin="and_(Comentario.id==Reacao.origem_id, Reacao.origem=='Comentario')", foreign_keys="[Reacao.origem_id]", lazy='dynamic', cascade="all, delete-orphan")
    spoiler = db.Column(db.Boolean, default=False)
    origem = db.Column(SAEnum(OrigemComentario), nullable=False, default=OrigemComentario.Livro)
    origem_id = db.Column(db.Integer)
    comentario_pai_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=True)
    comentarios = db.relationship('Comentario', backref=db.backref('comentario_pai', remote_side=[id]), lazy='dynamic')
    nivel_comentario = db.Column(db.Integer, default = 1)
    usuario_reagiu = False

    def dicionario(self):
        return {
            'id': self.id,
            'usuario': {
                'id': self.usuario.id,
                'nome': self.usuario.nome,
                'img': self.usuario.img
            },
            'conteudo': self.conteudo,
            'spoiler': self.spoiler,
            'nivel': self.nivel_comentario,
            'origem': str(self.origem.name).lower(),
            'origem_id': self.origem_id,
            'usuario_reagiu': self.usuario_reagiu,
            'reacoes': [] if self.reacoes is None else [r.dicionario() for r in self.reacoes],
            'tem_respostas': self.comentarios.count()
        }
    
    def validar_campos(self):
        msg_erro = ""

        if self.conteudo == "":
            msg_erro += "O conteúdo não pode estar vazio\n"
        elif len(self.conteudo) > 2000:
            msg_erro += "O conteúdo não pode ter mais do que 2000 caracteres\n"

        return msg_erro
    
    def procurar_usuario_reagiu(self, usuario):
        self.usuario_reagiu = Reacao.query.filter_by(
            usuario_id=usuario.id,
            origem=OrigemReacao.Comentario,
            origem_id=self.id
        ).first() is not None


@event.listens_for(Comentario, 'load')
def receive_load(comentario, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            comentario.procurar_usuario_reagiu(current_user)
    except Exception:
        pass