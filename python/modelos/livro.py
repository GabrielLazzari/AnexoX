
from datetime import datetime

from unidecode import unidecode

from python.banco import db
from python.modelos.usuario import *


class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(1000), nullable=False, default="")
    titulo_aux = db.Column(db.String(1000), nullable=False, default="")
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    editora_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    autor = db.relationship('Usuario', foreign_keys=[autor_id])
    editora = db.relationship('Usuario', foreign_keys=[editora_id])
    data_publicacao = db.Column(db.DateTime, default=datetime.min)
    descricao = db.Column(db.Text, nullable=True, default="")
    img = db.Column(db.String(256), nullable=True, default="")
    isbn = db.Column(db.String(13), nullable=True, default="")

    data_gravacao = db.Column(db.DateTime, default=datetime.now())

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


import sqlite3
from python.imagem import gravar_imagem
def garvar_livros_aux():
    with sqlite3.connect('G:\\Meu Drive\\Python\\Livros\\livros.db') as conexao:
        cursor = conexao.cursor()

        cursor.execute("select nome, img, dataLancamento, descricao, autor, editora from livros;")

        for livro in cursor.fetchall():
            nome = formatar_titulo_livro(livro[0])

            obj_autor = retornar_autor(livro[4])
            obj_editora = retornar_editora(livro[5])

            caminho_img = gravar_imagem(nome, livro[1], 'templates\\static\\imagens\\livros')
            caminho_img = caminho_img.replace("templates\\", "")
            try:
                data_publicacao = datetime.strptime(livro[2], '%d/%m/%Y')
            except:
                data_publicacao = datetime.min

            obj_livro = Livro(
                titulo = nome,
                titulo_aux = unidecode(nome).lower(),
                autor = obj_autor,
                editora = obj_editora,
                data_publicacao = data_publicacao,
                descricao = "" if livro[3] is None else "",
                isbn = "",
                img = caminho_img
            )

            livro_banco = db.session.query(Livro).filter_by(titulo=nome).first()

            if livro_banco is None:
                db.session.add(obj_livro)
                db.session.commit()


def retornar_autor(nome):
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


