from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event

from python.banco import db


class TipoNotificacao(PyEnum):
    SugestaoLivro = 0
    ConviteChat = 1
    UsuarioSeguindo = 2
    ComentarioLivro = 3
    ReacaoComentarioLivro = 4
    ComentarioPublicacao = 5
    ReacaoComentarioPublicacao = 6
    ReacaoPublicacao = 7
    SeguirLista = 8
    DeixarSeguirLista = 9
    LivroListaLivroAdicionado = 10
    LivroListaLivroDuplicado= 11
    LivroListaLivroMovido = 12
    LivroListaLivroRemovido = 13
    ListaLivroRemovida = 14


class Notificacao(db.Model):
    __tablename__ = 'notificacao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario_interagiu_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    titulo = db.Column(db.String(100), nullable=True, default="")
    conteudo = db.Column(db.String(1000), nullable=True, default="")
    img = db.Column(db.String(256), nullable=True, default="")
    tipo = db.Column(SAEnum(TipoNotificacao), nullable=False, default=TipoNotificacao.SugestaoLivro)
    lido = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500), nullable=True, default="")
    obj_id = db.Column(db.Integer)
    obj_interacao = None
    data_gravacao = db.Column(db.DateTime, default=datetime.now)

    def dicionario(self):
        return {
            'id': self.id,
            'link': self.link,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'img': self.img if self.img is not None and str(self.img).strip() != "" else 'static\\imagens\\usuarios\\anonimo.png',
            'data': self.data_gravacao.strftime('%d/%m/%Y') if self.data_gravacao else '',
            'hora': self.data_gravacao.strftime('%H:%M') if self.data_gravacao else '',
        }
    
    def carregar_obj(self, usuario):
        if self.tipo == TipoNotificacao.ComentarioLivro:
            pass


@event.listens_for(Notificacao, 'load')
def receive_load(notificacao, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            notificacao.carregar_obj(current_user)
    except Exception:
        pass
