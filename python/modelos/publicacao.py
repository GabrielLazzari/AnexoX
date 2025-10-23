from datetime import datetime
from enum import Enum as PyEnum

from python.modelos.notificacao import Notificacao, TipoNotificacao
from sqlalchemy import Enum as SAEnum, event

from python.banco import db
from python.modelos.reacao import OrigemReacao, Reacao, ReacaoTipo


class Visibilidade(PyEnum):
    Privada = 0
    Seguindo = 1
    Publica = 2


class Publicacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_gravacao = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    conteudo = db.Column(db.String(5000), nullable=True, default="")
    reacoes = db.relationship('Reacao', primaryjoin="and_(Publicacao.id==Reacao.origem_id, Reacao.origem=='Publicacao')", foreign_keys="[Reacao.origem_id]", lazy='dynamic', cascade="all, delete-orphan")
    usuario_reagiu = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        return {
            'id': self.id,
            'conteudo': self.conteudo,
            'data': self.data_gravacao.strftime('%d/%m/%Y') if self.data_gravacao else None,
            'hora': self.data_gravacao.strftime('%H:%M') if self.data_gravacao else None,
            'usuario': {
                'id': self.usuario.id if self.usuario is not None else '',
                'nome': self.usuario.nome if self.usuario is not None else '',
                'img': self.usuario.img if self.usuario is not None else ''
            },
            'usuario_reagiu': self.usuario_reagiu
        }

    def validar_campos(self):
        msg_erro = ""

        if len(self.conteudo) > 5000:
            msg_erro += "O conteúdo nao pode ser maior do que 5000\n"

        return msg_erro
    
    def reagir(self, usuario_contexto):
        reacao_banco = db.session.query(Reacao).filter_by(usuario_id=usuario_contexto.id, origem_id=self.id, origem=OrigemReacao.Publicacao).first()
        if reacao_banco:
            db.session.delete(reacao_banco)
        else:
            reacao = Reacao(
                usuario_id = usuario_contexto.id,
                origem_id = self.id,
                origem = OrigemReacao.Publicacao,
                reacao = db.session.query(ReacaoTipo).filter_by(nome="Coração").first()
            )

            db.session.add(reacao)

            if self.usuario_id != usuario_contexto.id:
                tipo = TipoNotificacao.ReacaoComentarioPublicacao
                link = f"publicacao?id={self.id}"

                notificacao_banco = Notificacao.query.filter_by(usuario_id=self.usuario_id, tipo=tipo, link=link).first()

                if notificacao_banco is None:
                    notificacao = Notificacao(
                        usuario_id = self.usuario_id,
                        usuario_interagiu_id = usuario_contexto.id,
                        titulo = "Reação em publicação",
                        conteudo = f"{usuario_contexto.nome} reagiu a sua publicacao.",
                        img = usuario_contexto.img,
                        tipo = tipo,
                        link = "",
                        obj_id = self.id
                    )
                    db.session.add(notificacao)

        db.session.commit()

    def procurar_usuario_reagiu(self, usuario):
        self.usuario_reagiu = Reacao.query.filter_by(
            usuario_id=usuario.id,
            origem=OrigemReacao.Publicacao,
            origem_id=self.id
        ).first() is not None

    def excluir(self):
        msg_erro = ""

        return msg_erro


class ListaPublicacaoPublicacao(db.Model):
    __tablename__ = 'lista_publicacao_publicacao'
    id = db.Column(db.Integer, primary_key=True)
    id_listapublicacao = db.Column(db.Integer, db.ForeignKey('lista_publicacao.id'))
    id_publicacao = db.Column(db.Integer, db.ForeignKey('publicacao.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    publicacao = db.relationship('Publicacao', backref='lista_publicacao_publicacao')
    data_criacao = db.Column(db.DateTime, default=datetime.now)


class ListaPublicacao(db.Model):
    __tablename__ = 'lista_publicacao'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="")
    descricao = db.Column(db.String(1000), nullable=True, default="")
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    visibilidade = db.Column(SAEnum(Visibilidade), nullable=False, default=Visibilidade.Privada)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    publicacoes = db.relationship('Publicacao', secondary=ListaPublicacaoPublicacao.__table__, lazy='dynamic')
    seguindo = False  # Usado apenas para indicar se o usuario logado esta seguindo esta lista

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao
        }

    def validar_campos(self):
        msg_erro = ""

        if self.nome.strip() == "":
            msg_erro += "O nome deve ser preenchido\n"
        elif len(self.nome) > 100:
            msg_erro += "O nome não pode ser maior do que 100 caracteres\n"

        if len(self.descricao) > 100:
            msg_erro += "A descrição não pode ser maior do que 1000 caracteres\n"

        return msg_erro

    def controle_lista_publicacao(self):

        if (erro_campos := self.validar_campos()) != "":
            return erro_campos

        msg_erro = ""

        mesmo_nome = db.session.query(ListaPublicacao).filter(ListaPublicacao.id!=self.id, ListaPublicacao.nome==self.nome).first()
        if mesmo_nome:
            return f"Já existe uma lista cadastrada com o nome '{mesmo_nome}'"

        print("atual", [self.id, self.nome, self.descricao])

        if not hasattr(self, 'id') or self.id is None:
            db.session.add(self)
            db.session.flush()
        
        db.session.commit()

        return msg_erro
    
    def excluir(self):
        db.session.delete(self)
        db.session.commit()

        return ""

    def vincular_publicacao(self, idPublicacao):
        publicacao = db.session.query(Publicacao).filter_by(id=idPublicacao).first()
        if not publicacao:
            return 'A publicação não existe ou foi alterada.'
        
        publicacaoListaBanco = db.session.query(ListaPublicacaoPublicacao).filter_by(id_listapublicacao=self.id, id_publicacao=idPublicacao, usuario_id=self.usuario_id).first()
        if publicacaoListaBanco:
            return "A publicação já está salva na lista '" + self.nome + "'"

        publicacaoLista = ListaPublicacaoPublicacao(
            id_listapublicacao = self.id,
            id_publicacao = idPublicacao,
            usuario_id = self.usuario_id
        )

        db.session.add(publicacaoLista)
        db.session.commit()

        return ''
    
    def excluir_publicacao(self, idPublicacao):
        publicacaoListaBanco = db.session.query(ListaPublicacaoPublicacao).filter_by(id_listapublicacao=self.id, id_publicacao=idPublicacao, usuario_id=self.usuario_id).first()
        if not publicacaoListaBanco:
            return "A publicação não está salva na lista '" + self.nome + "'"

        db.session.delete(publicacaoListaBanco)
        db.session.commit()

        return ''


@event.listens_for(Publicacao, 'load')
def receive_load(publicacao, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            publicacao.procurar_usuario_reagiu(current_user)
    except Exception:
        pass
