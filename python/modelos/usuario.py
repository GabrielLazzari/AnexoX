import base64
from datetime import datetime
from enum import Enum as PyEnum
import hashlib
import os

from flask_login import UserMixin
from flask import request as flask_request
from PIL import Image
import qrcode
from sqlalchemy import Enum as SAEnum, event
from unidecode import unidecode
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from python.banco import db
from python.imagem import gravar_imagem
from python.modelos.genero_literario import GeneroLiterario, PreferenciasLiterariasUsuario
from python.modelos.notificacao import Notificacao, TipoNotificacao
from python.modelos.recomendacao import alterar_pessoa_em_alta


def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()


class TipoUsuario(PyEnum):
    Leitor = 0
    Autor = 1
    Editora = 2


class AcaoLogPreferencia(PyEnum):
    Inserido = 0
    Excluido = 1


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False, default="")
    nome_aux = db.Column(db.String(256), nullable=False, default="")  # Pra pesquisa por nome sem acentuacao
    nome_alternativo = db.Column(db.String(256), nullable=True, default="")
    senha = db.Column(db.String(), default="")
    senha_confirmar = ""
    sentimento = db.Column(db.String(150), nullable=True, default="")
    descricao = db.Column(db.String(2000), nullable=True, default="")
    tipo = db.Column(SAEnum(TipoUsuario), nullable=False, default=TipoUsuario.Leitor)
    img = db.Column(db.String(256), nullable=True, default="")
    img_obj = None  # Pra quando procurar livros na internet e ainda nao gravar o livro no banco, tambem nao grava o usuario
    email = db.Column(db.String(100), nullable=True, default="")
    cnpj = db.Column(db.String(14), nullable=True, default="")
    notificacoes = db.Column(db.Boolean, default=True)
    notificar_livro = db.Column(db.Boolean, default=True)
    notificar_usuario_seguindo = db.Column(db.Boolean, default=True)
    notificar_lista_seguindo = db.Column(db.Boolean, default=True)
    verificado = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    preferencias_literarias = db.relationship('GeneroLiterario', secondary=PreferenciasLiterariasUsuario.__table__)
    seguindo = False  # Usado apenas para indicar se o usuario logado esta seguindo este usuario
    seguidor = False
    qtd_seguindo = 0
    qtd_seguidores = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self, usuario_tela_logado=False):
        return {
            'id': self.id,
            'ativo': True if self.senha != "" else False,
            'nome': self.nome,
            'img': self.img.replace("\\", "/") if self.img != "" else "static\\imagens\\usuarios\\anonimo.png",
            'email': self.email,
            'cnpj': self.cnpj,
            'tipo': self.tipo.value,
            'preferencias': ";".join([p if isinstance(p, str) else p.nome for p in self.preferencias_literarias]),
            'qr_compartilhar': self.gerar_qrcode_compartilhar(),
            'usuario_tela_logado': usuario_tela_logado,
            'seguindo': self.seguindo,
            'seguidor': self.seguidor,
            'qtd_seguindo': self.qtd_seguindo,
            'qtd_seguidores': self.qtd_seguidores
        }

    def validar_campos(self):
        msg_erro = ""

        self.nome = self.nome.strip()
        self.email = self.email.strip()

        if self.nome == "":
            msg_erro += "O nome não pode estar vazio\n"
        elif len(self.nome) > 256:
            msg_erro += "O nome não pode ter mais do que 256 caracteres\n"

        msg_erro += self.validar_senha()

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

        if self.id is None or (self.senha.strip() != "" or self.senha_confirmar.strip() != ""):
            if self.senha.strip() == "":
                msg_erro += "A senha não pode estar vazia\n"
            elif len(self.senha) > 256:
                msg_erro += "A senha não pode ter mais do que 256 caracteres\n"

            if self.senha != self.senha_confirmar:
                msg_erro += "A confirmação da senha está diferente da senha\n"

        return msg_erro

    def gravar(self):
        img_aux = self.img
        # Isso nao funciona, quando da um erro ao gravar como posso mandar a img do usuario de volta para tela???
        if isinstance(self.img, FileStorage):
            self.img = base64.b64encode(self.img.read()).decode("utf-8")

        msg_erro = self.validar_campos()
        if msg_erro != "":
            return msg_erro
        
        preferencias_aux = self.preferencias_literarias
        self.img = ""
        self.preferencias_literarias = []

        usuario_banco = db.session.query(Usuario).filter_by(id=self.id).first()
        self.nome_aux = "|" + unidecode(self.nome.lower().replace(" ", "")) + "|"
        if usuario_banco:
            usuario_banco.nome = self.nome
            usuario_banco.nome_aux = self.nome_aux
            usuario_banco.email = self.email
            usuario_banco.cnpj = self.cnpj
            usuario_banco.tipo = self.tipo
            usuario_banco.atualizar_caminho_imagem(img_aux, 'templates\\static\\imagens\\usuarios')
            usuario_banco.atualizar_preferencias(preferencias_aux)
            if self.senha.strip() != "" and hash(self.senha) != usuario_banco.senha:
                usuario_banco.senha = hash(self.senha)
            self = usuario_banco

        else:
            if db.session.query(Usuario).filter_by(nome=self.nome).first():
                return "Já existe um usuário cadastrado com esse nome"
            
            self.senha = hash(self.senha)
            db.session.add(self)
            db.session.flush()
            self.atualizar_caminho_imagem(img_aux, 'templates\\static\\imagens\\usuarios')
            self.atualizar_preferencias(preferencias_aux)

        db.session.commit()

        return msg_erro

    def excluir(self):
        db.session.delete(self)
        db.session.commit()

    def atualizar_caminho_imagem(self, imagem, caminho_base):
        if imagem and imagem != '':
            caminho_imagem = os.path.join(caminho_base, str(self.id))
            caminho_imagem = gravar_imagem("Perfil", imagem, caminho_imagem, transformar="perfil")
            caminho_imagem = caminho_imagem.replace("templates\\", "")

            self.img = caminho_imagem

    def atualizar_preferencias(self, preferencias_literarias):
        preferencias_literarias = list(map(lambda x: x.strip(), preferencias_literarias))
        tipos = GeneroLiterario.query.filter(GeneroLiterario.nome.in_(preferencias_literarias)).all()
        self.preferencias_literarias = tipos # ou preferencias_literarias.tipos.extend(tipos) se quiser manter os anteriores

    def gerar_qrcode_compartilhar(self):
        caminho_base = os.path.join(os.getcwd(), "templates\\static\\imagens\\usuarios\\", str(self.id))
        caminho = os.path.join(caminho_base, "perfil_qrcode.png")
        caminho_estatico = os.path.join("static", "imagens", "usuarios", str(self.id), "perfil_qrcode.png")
        print(os.getcwd())
        print(caminho)
        print(caminho_estatico)
        if not os.path.exists(caminho_base):
            return ""

        #if os.path.exists(caminho):
        #    return caminho_estatico

        qr = qrcode.QRCode(
            version=1,  # Tamanho do QR Code (1 é o menor)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nível de correção de erro
            box_size=10,  # Tamanho de cada "caixa" no QR Code
            border=4,  # Tamanho da borda
        )

        qr.add_data(flask_request.host_url + f"usuario?id={self.id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(caminho)
        return caminho_estatico

    def controle_seguir_usuario(self, usuario_seguir_id):
        seguindo = False

        if self.id == usuario_seguir_id:
            return "Não é possível seguir você mesmo.", seguindo
        
        usuario_seguir = db.session.query(Usuario).filter_by(id=usuario_seguir_id).first()
        if not usuario_seguir:
            return "O usuário que você está tentando seguir não existe.", seguindo

        ja_seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=self.id, usuario_seguindo_id=usuario_seguir_id).first()
        if ja_seguindo:
            db.session.delete(ja_seguindo)

        else:
            novo_seguindo = UsuarioSeguir(
                usuario_seguidor_id=self.id,
                usuario_seguindo_id=usuario_seguir_id,
            )

            if self.notificacoes and self.notificar_usuario_seguindo and usuario_seguir.senha != "":
                link = f"usuario?id={self.id}"
                notificacao_banco = Notificacao.query.filter_by(usuario_id=usuario_seguir.id, tipo=TipoNotificacao.UsuarioSeguindo, link=link).order_by(Notificacao.data_gravacao.desc()).first()
                if notificacao_banco is None:
                    notificacao = Notificacao(
                        usuario_id = usuario_seguir.id,
                        usuario_interagiu_id = self.id,
                        titulo = "Novo seguidor",
                        conteudo = f"{self.nome} começou a seguir você.",
                        img = self.img,
                        tipo =  TipoNotificacao.UsuarioSeguindo,
                        link = link
                    )
                    db.session.add(notificacao)

            db.session.add(novo_seguindo)
            seguindo = True
        
        alterar_pessoa_em_alta(self.id, usuario_seguir.id, seguindo=seguindo)

        db.session.commit()

        return "", seguindo
    
    def atualizar_status_seguimento(self, usuario_contexto):
        try:
            self.qtd_seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=self.id).count()
            self.qtd_seguidores = UsuarioSeguir.query.filter_by(usuario_seguindo_id=self.id).count()

            if not usuario_contexto or not hasattr(usuario_contexto, 'id'):
                self.seguindo = False
                self.seguidor = False
                return

            self.seguindo = UsuarioSeguir.query.filter_by(
                usuario_seguidor_id=usuario_contexto.id,
                usuario_seguindo_id=self.id
            ).first() is not None

            self.seguidor = UsuarioSeguir.query.filter_by(
                usuario_seguidor_id=self.id,
                usuario_seguindo_id=usuario_contexto.id
            ).first() is not None

        except Exception:
            self.seguindo = False
            self.seguidor = False
            self.qtd_seguindo = 0
            self.qtd_seguidores = 0

    def atualizar_preferencias_log(self, preferencias=None):
        if preferencias is None:
            preferencias = self.preferencias_literarias

        for preferencia in preferencias:
            pass
            

class PreferenciaLiterariaLog(db.Model):
    __tablename__ = 'preferencia_literaria_log'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    genero_literario_id = db.Column(db.Integer, db.ForeignKey('genero_literario.id'))
    genero_literario = db.relationship('GeneroLiterario', foreign_keys=[genero_literario_id])
    data_gravacao = db.Column(db.DateTime, default=datetime.min)
    acao = db.Column(SAEnum(AcaoLogPreferencia), nullable=False, default=AcaoLogPreferencia.Inserido)


class UsuarioSeguir(db.Model):
    __tablename__ = 'usuario_seguir'
    id = db.Column(db.Integer, primary_key=True)
    usuario_seguidor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # eu usuario
    usuario_seguindo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # estou seguindo outro usuario
    data_gravacao = db.Column(db.DateTime, default=datetime.now)

    usuario_seguidor = db.relationship(
        'Usuario',
        foreign_keys=[usuario_seguidor_id]
    )

    usuario_seguindo = db.relationship(
        'Usuario',
        foreign_keys=[usuario_seguindo_id]
    )


@event.listens_for(Usuario, 'load')
def receive_load(usuario, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            usuario.atualizar_status_seguimento(current_user)
    except Exception:
        pass
