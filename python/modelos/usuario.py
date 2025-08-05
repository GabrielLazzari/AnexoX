from datetime import datetime
from enum import Enum as PyEnum
import os

from flask_login import UserMixin
from PIL import Image
from sqlalchemy import Enum as SAEnum, event
from werkzeug.utils import secure_filename

from python.banco import db
from python.imagem import gravar_imagem


class TipoUsuario(PyEnum):
    Leitor = 0
    Autor = 1
    Editora = 2


class PreferenciasLiterarias(db.Model):
    __tablename__ = 'preferencia_literaria'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    id_genero_literario = db.Column(db.Integer, db.ForeignKey('genero_literario.id'))


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False, default="")
    senha = db.Column(db.String(), default="")
    senha_confirmar = ""
    tipo = db.Column(SAEnum(TipoUsuario), nullable=False, default=TipoUsuario.Leitor)
    img = db.Column(db.String(256), nullable=True, default="")
    email = db.Column(db.String(100), nullable=True, default="")
    cnpj = db.Column(db.String(14), nullable=True, default="")
    verificado = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.min)
    preferencias_literarias = db.relationship('GeneroLiterario', secondary=PreferenciasLiterarias.__table__, back_populates='usuarios')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'img': self.img,
        }

    def validar_campos(self):
        msg_erro = ""

        self.nome = self.nome.strip()
        self.email = self.email.strip()

        if self.nome == "":
            msg_erro += "O nome não pode estar vazio\n"
        elif len(self.nome) > 256:
            msg_erro += "O nome não pode ter mais do que 256 caracteres\n"

        if self.senha.strip() == "":
            msg_erro += "A senha não pode estar vazia\n"
        elif len(self.senha) > 256:
            msg_erro += "A senha não pode ter mais do que 256 caracteres\n"

        if self.senha != self.senha_confirmar:
            msg_erro += "A confirmação da senha está diferente da senha\n"

        if self.email == "":
            msg_erro += "O email não pode estar vazio\n"
        elif len(self.email) > 256:
            msg_erro += "O email não pode ter mais do que 100 caracteres\n"

        if self.tipo == TipoUsuario.Editora or self.tipo == TipoUsuario.Autor:
            self.cnpj = self.cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
            if self.cnpj == "":
                msg_erro += "O cnpj não pode estar vazio\n"
            elif len(self.cnpj) > 14:
                msg_erro += "O cnpj não pode ter mais do que 14 caracteres\n"

        return msg_erro

    def atualizar_caminho_imagem(self, imagem, caminho_base):
        if imagem and imagem.filename != '':
            caminho_imagem = os.path.join(caminho_base, str(self.id))
            caminho_imagem = gravar_imagem("Perfil", Image.open(imagem), caminho_imagem, False)
            caminho_imagem = caminho_imagem.replace("templates\\", "")

            self.img = caminho_imagem
            db.session.commit()

    def atualizar_preferencias(self, preferencias_literarias):
        preferencias_literarias = list(map(lambda x: x.strip(), preferencias_literarias))
        tipos = GeneroLiterario.query.filter(GeneroLiterario.descricao.in_(preferencias_literarias)).all()
        self.preferencias_literarias = tipos # ou preferencias_literarias.tipos.extend(tipos) se quiser manter os anteriores

        db.session.commit()


class GeneroLiterario(db.Model):
    __tablename__ = 'genero_literario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)

    usuarios = db.relationship('Usuario', secondary=PreferenciasLiterarias.__table__, back_populates='preferencias_literarias')


@event.listens_for(GeneroLiterario.__table__, 'after_create')
def inserir_generos_literarios_estaticos(target, connection, **kw):
    connection.execute(
        GeneroLiterario.__table__.insert(),
        [
            {"descricao": "Romance"},
            {"descricao": "Suspense"},
            {"descricao": "Mistério"},
            {"descricao": "Aventura"},
            {"descricao": "Policial"},
            {"descricao": "Ficção Científica"},
            {"descricao": "Fantasia"},
            {"descricao": "Técnicos / Estudos"},
            {"descricao": "Bibliográficos / Auto Bibliográficos"},
            {"descricao": "Terror"},
            {"descricao": "Auto Ajuda"},
            {"descricao": "Religioso"},
            {"descricao": "Finanças"},
            {"descricao": "Literatura"},
            {"descricao": "Infanto Juvenil"},
            {"descricao": "Contos"},
            {"descricao": "Poesia"},
            {"descricao": "Histórico"},
        ]
    )