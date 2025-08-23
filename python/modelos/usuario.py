from datetime import datetime
from enum import Enum as PyEnum
import os

from flask_login import UserMixin
from PIL import Image
import qrcode
from sqlalchemy import Enum as SAEnum, event
from werkzeug.utils import secure_filename

from python.banco import db
from python.imagem import gravar_imagem


class TipoUsuario(PyEnum):
    Leitor = 0
    Autor = 1
    Editora = 2


class AcaoLogPreferencia(PyEnum):
    Inserido = 0
    Excluido = 1


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
    img_obj = None  # Pra quando procurar livros na internet e ainda nao gravar o livro no banco, tambem nao grava o usuario
    email = db.Column(db.String(100), nullable=True, default="")
    cnpj = db.Column(db.String(14), nullable=True, default="")
    notificacoes = db.Column(db.Boolean, default=True)
    notificacoes_personalisadas = db.Column(db.Boolean, default=True)
    verificado = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.min)
    preferencias_literarias = db.relationship('GeneroLiterario', secondary=PreferenciasLiterarias.__table__, back_populates='usuarios')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self, usuario_tela_logado=False):
        return {
            'id': self.id,
            'nome': self.nome,
            'img': self.img.replace("\\", "/") if self.img != "" else "static\\imagens\\usuarios\\anonimo.png",
            'email': self.email,
            'cnpj': self.cnpj,
            'tipo': self.tipo.value,
            'preferencias': ";".join([p.descricao for p in self.preferencias_literarias]),
            'qr_compartilhar': self.gerar_qrcode_compartilhar(),
            'usuario_tela_logado': usuario_tela_logado
        }

    def validar_campos(self, usuario_autenticado=False):
        msg_erro = ""

        self.nome = self.nome.strip()
        self.email = self.email.strip()

        if self.nome == "":
            msg_erro += "O nome não pode estar vazio\n"
        elif len(self.nome) > 256:
            msg_erro += "O nome não pode ter mais do que 256 caracteres\n"

        if not usuario_autenticado:
            self.validar_senha()

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

    def validar_senha(self):
        msg_erro = ""

        if self.senha.strip() == "":
            msg_erro += "A senha não pode estar vazia\n"
        elif len(self.senha) > 256:
            msg_erro += "A senha não pode ter mais do que 256 caracteres\n"

        if self.senha != self.senha_confirmar:
            msg_erro += "A confirmação da senha está diferente da senha\n"

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

    def gerar_qrcode_compartilhar(self):
        caminho_base = os.path.join(os.getcwd(), "templates\\static\\imagens\\usuarios\\", str(self.id))
        caminho = os.path.join(caminho_base, "perfil_qrcode.png")
        caminho_estatico = os.path.join("static", "imagens", "usuarios", str(self.id), "perfil_qrcode.png")
        print(os.getcwd())
        print(caminho)
        print(caminho_estatico)
        if not os.path.exists(caminho_base):
            return ""

        if os.path.exists(caminho):
            return caminho_estatico

        qr = qrcode.QRCode(
            version=1,  # Tamanho do QR Code (1 é o menor)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nível de correção de erro
            box_size=10,  # Tamanho de cada "caixa" no QR Code
            border=4,  # Tamanho da borda
        )

        qr.add_data("teste")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(caminho)
        return caminho_estatico

    def seguir_usuario(self, usuario_seguir_id):
        if self.id == usuario_seguir_id:
            return "Não é possível seguir você mesmo."

        ja_seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=self.id, usuario_seguindo_id=usuario_seguir_id).first()
        if ja_seguindo:
            return "Você já está seguindo este usuário."

        novo_seguindo = UsuarioSeguir(
            usuario_seguidor_id=self.id,
            usuario_seguindo_id=usuario_seguir_id,
            data_gravacao=datetime.now()
        )
        
        db.session.add(novo_seguindo)
        db.session.commit()
        
        return ""
    
    def deixar_seguir_usuario(self, usuario_deixar_seguir_id):
        if self.id == usuario_deixar_seguir_id:
            return "Não é possível deixar de seguir você mesmo."

        seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=self.id, usuario_seguindo_id=usuario_deixar_seguir_id).first()
        if not seguindo:
            return "Você não está seguindo este usuário."

        db.session.delete(seguindo)
        db.session.commit()

        return ""


class PreferenciaLiterariaLog(db.Model):
    __tablename__ = 'preferencia_literaria_log'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    genero_literario_id = db.Column(db.Integer, db.ForeignKey('genero_literario.id'))
    genero_literario = db.relationship('GeneroLiterario', foreign_keys=[genero_literario_id])
    data_gravacao = db.Column(db.DateTime, default=datetime.min)
    acao = db.Column(SAEnum(AcaoLogPreferencia), nullable=False, default=AcaoLogPreferencia.Inserido)


class GeneroLiterario(db.Model):
    __tablename__ = 'genero_literario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    icone = db.Column(db.String(256), nullable=True, default="")

    usuarios = db.relationship('Usuario', secondary=PreferenciasLiterarias.__table__, back_populates='preferencias_literarias')


class UsuarioSeguir(db.Model):
    __tablename__ = 'usuario_seguir'
    id = db.Column(db.Integer, primary_key=True)
    usuario_seguidor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario_seguindo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data_gravacao = db.Column(db.DateTime, default=datetime.min)


@event.listens_for(GeneroLiterario.__table__, 'after_create')
def inserir_generos_literarios_estaticos(target, connection, **kw):
    connection.execute(
        GeneroLiterario.__table__.insert(),
        [
            {"descricao": "Romance", "icone": "static\\icones\\heart-outline.svg"},
            {"descricao": "Suspense", "icone": ""},
            {"descricao": "Mistério", "icone": "static\\icones\\footsteps-outline.svg"},
            {"descricao": "Aventura", "icone": ""},
            {"descricao": "Policial", "icone": ""},
            {"descricao": "Ficção Científica", "icone": ""},
            {"descricao": "Fantasia", "icone": ""},
            {"descricao": "Técnicos / Estudos", "icone": ""},
            {"descricao": "Bibliográficos / Auto Bibliográficos", "icone": ""},
            {"descricao": "Terror", "icone": ""},
            {"descricao": "Auto Ajuda", "icone": ""},
            {"descricao": "Religioso", "icone": ""},
            {"descricao": "Finanças", "icone": "static\\icones\\cash-outline.svg"},
            {"descricao": "Literatura", "icone": ""},
            {"descricao": "Infanto Juvenil", "icone": ""},
            {"descricao": "Contos", "icone": ""},
            {"descricao": "Poesia", "icone": ""},
            {"descricao": "Histórico", "icone": ""},
        ]
    )