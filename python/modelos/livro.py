
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event
from unidecode import unidecode

from python.banco import db
from python.modelos.usuario import *


class Visibilidade(PyEnum):
    Privada = 0
    Publica = 1
    Seguindo = 2


class Livro(db.Model):
    __tablename__ = 'livro'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(1000), nullable=False, default="")
    titulo_aux = db.Column(db.String(1000), nullable=False, default="")  # Pra pesquisa por titulo sem acentuacao
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    editora_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    autor = db.relationship('Usuario', foreign_keys=[autor_id])
    editora = db.relationship('Usuario', foreign_keys=[editora_id])
    data_publicacao = db.Column(db.DateTime, default=datetime.min)
    descricao = db.Column(db.Text, nullable=True, default="")
    img = db.Column(db.String(256), nullable=True, default="")
    img_obj = None  # Pra quando procurar livros na internet e ainda nao gravar o livro no banco
    isbn = db.Column(db.String(13), nullable=True, default="")
    qtd_paginas = db.Column(db.Integer, nullable=True, default=0)
    data_gravacao = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'img': self.img,
            'autor': self.autor.nome if self.autor is not None else '',
            'idAutor': self.autor.id if self.autor is not None else '',
            'editora': self.editora.nome if self.editora is not None else '',
            'idEditora': self.editora.id if self.editora is not None else '',
        }


class LivroPreco(db.Model):
    __tablename__ = 'livro_preco'
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    link_id = db.Column(db.Integer, db.ForeignKey('livro_link.id'))
    preco = db.Column(db.Float, nullable=True, default=0)
    data_consulta = db.Column(db.DateTime, default=datetime.min)


class LivroLink(db.Model):
    __tablename__ = 'livro_link'
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    link = db.Column(db.String(1000), nullable=False, default="")
    data_consulta = db.Column(db.DateTime, default=datetime.min)


class ListaLivroLivro(db.Model):
    __tablename__ = 'lista_livro_livro'
    id = db.Column(db.Integer, primary_key=True)
    id_listalivro = db.Column(db.Integer, db.ForeignKey('lista_livro.id'))
    id_livro = db.Column(db.Integer, db.ForeignKey('livro.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro = db.relationship('Livro', backref='lista_livro_livro')


class ListaLivro(db.Model):
    __tablename__ = 'lista_livro'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="")
    descricao = db.Column(db.String(1000), nullable=True, default="")
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    visibilidade = db.Column(SAEnum(Visibilidade), nullable=False, default=Visibilidade.Privada)
    data_criacao = db.Column(db.DateTime, default=datetime.now())
    livros = db.relationship('Livro', secondary=ListaLivroLivro.__table__)

    def dicionario(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'visibilidade': self.visibilidade.value,
            'usuario_id': self.usuario_id
        }

    def validar_campos(self):
        msg_erro = ""

        if self.nome.strip() == "":
            msg_erro += "O nome da lista não pode ser vazio.\n"
        elif len(self.nome) > 100:
            msg_erro += "O nome da lista não pode ter mais do que 100 caracteres.\n"

        if self.descricao is not None and len(self.descricao) > 1000:
            msg_erro += "A descrição da lista não pode ter mais do que 1000 caracteres.\n"

        return msg_erro

    def vincular_livro(self, idLista, idLivro, idUsuario):
        if idLivro is None or idLivro <= 0:
            return 'Livro não encontrado ou já excluído'

        livro = db.session.query(Livro).filter_by(id=idLivro).first()
        if livro is None:
            return 'Livro não encontrado ou já excluído'

        livro_lista = ListaLivroLivro(id_listalivro=idLista, id_livro=livro.id, usuario_id=idUsuario)

        livro_vinculado = db.session.query(ListaLivroLivro).filter_by(id_listalivro=livro_lista.id_listalivro, id_livro=livro.id, usuario_id=idUsuario).first()
        if livro_vinculado is not None:
            return 'Livro já vinculado a esta lista'

        db.session.add(livro_lista)
        db.session.commit()

        return ""
    
    def desvincular_livro(self, idLivro):
        livro_lista = db.session.query(ListaLivroLivro).filter_by(
            id_listalivro=self.id,
            id_livro=idLivro
        ).first()
        
        if livro_lista:
            db.session.delete(livro_lista)
            db.session.commit()

        return ""
    
    def mover_livro(self, idLivro, idListaMover):
        self.desvincular_livro(idLivro)
        return self.vincular_livro(idListaMover, idLivro, self.usuario_id)


def formatar_titulo_livro(titulo):
    titulo = titulo.strip().split(' ')
    titulo_aux = [titulo[0].strip().title()]
    for pos in range(1, len(titulo)):
        palavra = titulo[pos].strip()
        if palavra != "":
            if len(palavra) > 1 or titulo_aux[-1].endswith(":") or titulo_aux[-1].endswith(";"):
                titulo_aux.append(palavra.title())
            else:
                titulo_aux.append(palavra.lower())

    return " ".join(titulo_aux)


def gravar_livro(livro):

    livro_banco = db.session.query(Livro).filter_by(titulo=livro.titulo).first()

    if isinstance(livro.autor, str):
        livro.autor = retornar_usuario(livro.autor, TipoUsuario.Autor)

    if isinstance(livro.editora, str):
        livro.editora = retornar_usuario(livro.editora, TipoUsuario.Editora)

    autor_banco = db.session.query(Usuario).filter_by(nome=livro.autor.nome, tipo=TipoUsuario.Autor).first()
    if autor_banco is None:
        db.session.add(livro.autor)

    editora_banco = db.session.query(Usuario).filter_by(nome=livro.editora.nome, tipo=TipoUsuario.Editora).first()
    if editora_banco is None:
        db.session.add(livro.editora)

    if livro_banco is None:
        db.session.add(livro)
        db.session.commit()


def retornar_usuario(usuario, tipo=TipoUsuario.Leitor):
    if usuario is None or (isinstance(usuario, str) and usuario.strip() == ""):
        return None

    if isinstance(usuario, str):
        usuario = Usuario(nome=usuario.strip().title(), tipo=tipo)
    elif isinstance(usuario, Usuario):
        usuario.nome = usuario.nome.strip().title()
        usuario.tipo = tipo
    else:
        return None

    usuario_banco = db.session.query(Usuario).filter_by(nome=usuario.nome, tipo=tipo).first()

    if usuario_banco is not None:
        return usuario_banco

    return usuario


@event.listens_for(Usuario, 'after_insert')
def inserir_lista_livros_estaticos(mapper, connection, target):
    if target.tipo != TipoUsuario.Leitor and target.tipo != TipoUsuario.Autor:
        return
    
    connection.execute(
        ListaLivro.__table__.insert(),
        [
            {"usuario_id": target.id, "nome": "Já lidos", "descricao": "Livros que já li"},
            {"usuario_id": target.id, "nome": "Desejo ler", "descricao": "Livros que um dia quero ler"},
            {"usuario_id": target.id, "nome": "Estou lendo", "descricao": "Livros que estou lendo"},
            {"usuario_id": target.id, "nome": "Adquiridos", "descricao": "Livros que possuo"},
        ]
    )


import sqlite3
from python.imagem import gravar_imagem
def garvar_livros_aux():
    with sqlite3.connect('G:\\Meu Drive\\Python\\Livros\\livros.db') as conexao:
        cursor = conexao.cursor()

        cursor.execute("select nome, img, dataLancamento, descricao, autor, editora from livros;")

        for livro in cursor.fetchall():
            nome = formatar_titulo_livro(livro[0])

            caminho_img = gravar_imagem(nome, livro[1], 'templates\\static\\imagens\\livros')
            caminho_img = caminho_img.replace("templates\\", "")
            try:
                data_publicacao = datetime.strptime(livro[2], '%d/%m/%Y')
            except:
                data_publicacao = datetime.min

            obj_livro = Livro(
                titulo = nome,
                titulo_aux = unidecode(nome).lower(),
                autor = retornar_usuario(livro[4], TipoUsuario.Autor),
                editora = livro[5],
                data_publicacao = data_publicacao,
                descricao = "" if livro[3] is None else "",
                isbn = "",
                img = caminho_img
            )

            gravar_livro(obj_livro)


'''def retornar_autor(nome):
    if nome is None or nome.strip() == "":
        return None

    nome = nome.strip().title()

    autor_banco = db.session.query(Usuario).filter_by(nome=nome, tipo=TipoUsuario.Autor).first()

    if autor_banco is not None:
        return autor_banco

    else:
        obj_autor = Usuario(
            nome=nome,
            tipo=TipoUsuario.Autor
        )

        db.session.add(obj_autor)
        db.session.commit()

        return obj_autor


def retornar_editora(nome):
    if nome is None or nome.strip() == "":
        return None

    nome = nome.strip().title()

    editora_banco = db.session.query(Usuario).filter_by(nome=nome, tipo=TipoUsuario.Editora).first()

    if editora_banco is not None:
        return editora_banco

    else:
        obj_editora = Usuario(
            nome=nome,
            tipo=TipoUsuario.Editora
        )

        db.session.add(obj_editora)
        db.session.commit()

        return obj_editora
'''

