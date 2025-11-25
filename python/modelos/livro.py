
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum as SAEnum, event, or_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from sqlalchemy import select
from unidecode import unidecode

from python.banco import db
from python.modelos.genero_literario import GeneroLiterario, EstilosLiterariosLivro
from python.modelos.usuario import *
from python.modelos.recomendacao import alterar_livro_em_alta


class VisibilidadeLivro(PyEnum):
    Privada = 0
    Seguindo = 1
    Publica = 2


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
    estilos_literarios = db.relationship("GeneroLiterario", secondary="estilo_literario_livro", backref="as_")
    links = db.relationship('LivroLink', foreign_keys="[LivroLink.livro_id]", lazy='dynamic')
    data_gravacao = db.Column(db.DateTime, default=datetime.now)
    livro_salvo = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for column in self.__table__.columns:
            if isinstance(column.type, db.String) and column.name not in kwargs:
                setattr(self, column.name, column.default.arg if column.default is not None else "")

    def dicionario(self):
        print('eeesssss', [estilo.dicionario() for estilo in self.estilos_literarios])
        return {
            'id': self.id,
            'titulo': self.titulo,
            'img': self.img if self.img is not None and str(self.img).strip() != "" else 'static\\imagens\\sistema\\livro_vazio.jpg',
            'descricao': self.descricao,
            'data_publicacao': self.data_publicacao.strftime("%d/%m/%Y") if self.data_publicacao is not None and self.data_publicacao > datetime.min else '',
            'livro_salvo': self.livro_salvo,
            'autor': {
                'id': self.autor.id if self.autor is not None else '',
                'nome': self.autor.nome if self.autor is not None else '',
                'descricao': (self.autor.descricao if self.autor.descricao is not None else '') if self.autor is not None else '',
                'img': self.autor.img if self.autor is not None and str(self.autor.img).strip() != "" else 'static\\imagens\\usuarios\\anonimo.png'
            },
            'editora': {
                'id': self.editora.id if self.editora is not None else '',
                'nome': self.editora.nome if self.editora is not None else ''
            },
            'links': [link.dicionario() for link in self.links],
            'estilos': "; ".join([estilo.dicionario()['nome'] for estilo in self.estilos_literarios]).strip()
        }
    
    @hybrid_property
    def nome_autor(self):
        return '' if self.autor is None else self.autor.nome_aux

    @nome_autor.expression
    def nome_autor(cls):
        return (
            select(Usuario.nome)
            .where(Usuario.id == cls.autor_id)
            .correlate(cls)
            .scalar_subquery()
        )
    
    @hybrid_property
    def nome_editora(self):
        return '' if self.editora is None else self.editora.nome_aux

    @nome_editora.expression
    def nome_editora(cls):
        return (
            select(Usuario.nome)
            .where(Usuario.id == cls.editora_id)
            .correlate(cls)
            .scalar_subquery()
        )

    def atualizar_caminho_imagem(self, imagem):
        if imagem and imagem != '':
            nome = formatar_titulo_livro(self.titulo)
            caminho_imagem = "templates\\static\\imagens\\livros"
            caminho_imagem = gravar_imagem(nome, imagem, caminho_imagem, transformar="livro")
            caminho_imagem = caminho_imagem.replace("templates\\", "")

            self.img = caminho_imagem
            db.session.commit()

    def procurar_livro_salvo(self, usuario_contexto):
        self.livro_salvo = ListaLivroLivro.query.filter_by(
            id_livro=self.id,
            usuario_id=usuario_contexto.id
        ).first() is not None


class LivroPreco(db.Model):
    __tablename__ = 'livro_preco'
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    link_id = db.Column(db.Integer, db.ForeignKey('livro_link.id'))
    preco = db.Column(db.Float, nullable=True, default=-1)
    preco_usado = db.Column(db.Float, nullable=True, default=-1)
    data_consulta = db.Column(db.DateTime, default=datetime.now)


def str_to_float(valor):
    try:
        return float("{:.2f}".format(float(str(valor).replace(",", "."))))
    except:
        return -1


def controle_livro_preco(livro_id, link_id, preco, preco_usado=-1):
    livro_banco = db.session.query(Livro).filter_by(id=livro_id).first()
    if livro_banco is None:
        return False
    
    preco = str_to_float(preco)
    preco_usado = str_to_float(preco_usado)

    if preco == -1 and preco_usado == -1:
        return False

    livro_preco = db.session.query(LivroPreco).filter_by(livro_id=livro_id, link_id=link_id).order_by(LivroPreco.data_consulta.desc()).first()

    print(livro_preco is None, livro_preco.preco, preco, livro_preco.preco_usado, preco_usado)
    print(livro_preco.preco != preco, preco != -1, livro_preco.preco_usado != preco_usado, preco_usado != -1)

    if livro_preco is None or (livro_preco.preco != preco and preco != -1) or (livro_preco.preco_usado != preco_usado and preco_usado != -1):
        novo_livro_preco = LivroPreco(
            livro_id = livro_id,
            link_id = link_id,
            preco = preco,
            preco_usado = preco_usado
        )

        db.session.add(novo_livro_preco)

        return True
    
    # Query para apagar registros duplicados
    # delete FROM livro_preco
    # WHERE id NOT IN (
    #     SELECT id FROM (
    #         SELECT id
    #         FROM livro_preco AS lp
    #         WHERE lp.data_consulta = (
    #             SELECT MIN(data_consulta)
    #             FROM livro_preco AS sub
    #             WHERE sub.livro_id = lp.livro_id
    #             AND sub.link_id = lp.link_id
    #             AND sub.preco = lp.preco
    #         )
    #     )
    # );

    return False


class LivroLink(db.Model):
    __tablename__ = 'livro_link'
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    link = db.Column(db.String(1000), nullable=False, default="")
    hospedeiro = db.Column(db.String(500), nullable=False, default="")
    data_consulta = db.Column(db.DateTime, default=datetime.now)

    def dicionario(self):
        return {
            'livro_id': self.livro_id,
            'link': self.link,
            'hospedeiro': self.hospedeiro
        }


def controle_livro_link(livro_id, hospedeiro, link):
    if link.strip() == "":
        return None
    
    livro_link = db.session.query(LivroLink).filter_by(livro_id=livro_id, hospedeiro=hospedeiro).first()
    if livro_link:
        livro_link.link = link
    else:
        livro_link = LivroLink(
            livro_id = livro_id,
            link = link,
            hospedeiro= hospedeiro
        )

        db.session.add(livro_link)
        db.session.flush()

    return livro_link


class ListaLivroLivro(db.Model):
    __tablename__ = 'lista_livro_livro'
    id = db.Column(db.Integer, primary_key=True)
    id_listalivro = db.Column(db.Integer, db.ForeignKey('lista_livro.id'))
    id_livro = db.Column(db.Integer, db.ForeignKey('livro.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro = db.relationship('Livro', backref='lista_livro_livro')
    data_criacao = db.Column(db.DateTime, default=datetime.now)


class ListaLivro(db.Model):
    __tablename__ = 'lista_livro'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="")
    descricao = db.Column(db.String(1000), nullable=True, default="")
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    visibilidade = db.Column(SAEnum(VisibilidadeLivro), nullable=False, default=VisibilidadeLivro.Privada)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    livros = db.relationship('Livro', secondary=ListaLivroLivro.__table__, lazy='dynamic')
    seguindo = False  # Usado apenas para indicar se o usuario logado esta seguindo esta lista
    seguidores = db.relationship('ListaSeguir', foreign_keys="[ListaSeguir.lista_id]", lazy='dynamic', cascade='all, delete-orphan')

    def dicionario(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'visibilidade': self.visibilidade.value,
            'usuario_id': self.usuario_id,
            'seguindo': self.seguindo
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

    def apagar_lista(self, usuario_contexto):
        msg_erro = ""

        for usuario_lista_seguir in db.session.query(ListaSeguir).filter_by(usuario_seguindo_id=usuario_contexto.id, lista_id=self.id).all():
            usuario_notificar = db.session.query(Usuario).filter_by(id=usuario_lista_seguir.usuario_seguidor_id).first()

            if usuario_notificar is None:
                continue

            if usuario_notificar.notificacoes and usuario_notificar.notificar_lista_seguindo and usuario_notificar.senha != "":
                link = f"usuario?id={usuario_contexto.id}&idLista={self.id}"
                notificacao_banco = Notificacao.query.filter_by(usuario_id=usuario_notificar.id, tipo=TipoNotificacao.ListaLivroRemovida, link=link).order_by(Notificacao.data_gravacao.desc()).first()
                if notificacao_banco is None:
                    notificacao = Notificacao(
                        usuario_id = usuario_notificar.id,
                        usuario_interagiu_id = usuario_contexto.id,
                        titulo = "Lista de livro removida",
                        conteudo = f"{usuario_contexto.nome} excluiu a lista '{self.nome}'. As notificações nunca mais aparecerão.",
                        img = usuario_contexto.img,
                        tipo = TipoNotificacao.ListaLivroRemovida,
                        link = link,
                        obj_id = self.id
                    )
                    db.session.add(notificacao)

        db.session.delete(self)
        db.session.commit()

        return msg_erro

    def vincular_livro(self, idLista, idLivro, usuario_contexto, mover=False):
        if idLivro is None or int(idLivro) <= 0:
            return 'Livro não encontrado ou já excluído'

        livro = db.session.query(Livro).filter_by(id=idLivro).first()
        if livro is None:
            return 'Livro não encontrado ou já excluído'

        lista_mover = None
        if self.id != int(idLista):
            lista_mover = db.session.query(ListaLivro).filter_by(id=idLista, usuario_id=usuario_contexto.id).first()
            if lista_mover is None:
                return 'A lista para mover o livro não existe ou foi alterada'

        livro_lista = ListaLivroLivro(id_listalivro=idLista, id_livro=livro.id, usuario_id=usuario_contexto.id)

        livro_vinculado = db.session.query(ListaLivroLivro).filter_by(id_listalivro=livro_lista.id_listalivro, id_livro=livro.id, usuario_id=usuario_contexto.id).first()
        if livro_vinculado is not None:
            return 'Livro já vinculado a esta lista'

        alterar_livro_em_alta(usuario_contexto.id, idLivro, adicionado=True)

        db.session.add(livro_lista)

        if mover:
            notificar_movimentacao_livro(self, lista_mover, usuario_contexto, livro, TipoNotificacao.LivroListaLivroAdicionado)
        else:
            notificar_movimentacao_livro(self, None, usuario_contexto, livro, TipoNotificacao.LivroListaLivroAdicionado)

        return ""
    
    def desvincular_livro(self, idLivro, usuario_contexto, mover=False):
        livro_lista = db.session.query(ListaLivroLivro).filter_by(
            id_listalivro=self.id,
            id_livro=idLivro
        ).first()
        
        if livro_lista:
            alterar_livro_em_alta(livro_lista.usuario_id, idLivro, adicionado=False)
            db.session.delete(livro_lista)

            if not mover:
                livro = db.session.query(Livro).filter_by(id=idLivro).first()
                notificar_movimentacao_livro(self, None, usuario_contexto, livro, TipoNotificacao.LivroListaLivroRemovido)

        return ""
    
    def mover_livro(self, idLivro, idListaMover, usuario_contexto):
        self.desvincular_livro(idLivro, usuario_contexto, mover=True)
        return self.vincular_livro(idListaMover, idLivro, usuario_contexto, mover=True)

    def controle_seguir_lista(self, usuario_contexto):
        seguindo = False

        usuario_seguir = db.session.query(Usuario).filter_by(id=self.usuario_id).first()
        if not usuario_seguir:
            return "O usuário que você está tentando seguir a lista não existe.", seguindo

        ja_seguindo = ListaSeguir.query.filter_by(lista_id=self.id, usuario_seguidor_id=usuario_contexto.id, usuario_seguindo_id=self.usuario_id).first()
        if ja_seguindo:
            db.session.delete(ja_seguindo)
        else:
            novo_seguindo = ListaSeguir(
                usuario_seguidor_id=usuario_contexto.id,
                usuario_seguindo_id=self.usuario_id,
                lista_id=self.id
            )

            if usuario_seguir.notificacoes and usuario_seguir.notificar_lista_seguindo and usuario_seguir.senha != "":
                link = f"usuario?id={usuario_contexto.id}&idLista={self.id}"
                notificacao_banco = Notificacao.query.filter_by(usuario_id=usuario_seguir.id, tipo=TipoNotificacao.SeguirLista, link=link).order_by(Notificacao.data_gravacao.desc()).first()
                if notificacao_banco is None:
                    notificacao = Notificacao(
                        usuario_id = usuario_seguir.id,
                        usuario_interagiu_id = usuario_contexto.id,
                        titulo = "Novo seguidor na lista",
                        conteudo = f"{usuario_contexto.nome} está seguindo sua lista '{self.nome}'.",
                        img = usuario_contexto.img,
                        tipo =  TipoNotificacao.SeguirLista,
                        link = link,
                        obj_id = self.id
                    )
                    db.session.add(notificacao)

            db.session.add(novo_seguindo)
            seguindo = True

        db.session.commit()

        return "", seguindo
    
    def atualizar_status_seguimento(self, usuario_contexto):
        try:
            self.seguindo = ListaSeguir.query.filter_by(
                usuario_seguidor_id=usuario_contexto.id,
                usuario_seguindo_id=self.usuario_id,
                lista_id=self.id
            ).first() is not None

        except Exception:
            self.seguindo = False


def notificar_movimentacao_livro(lista_atual, lista_nova, usuario_contexto, livro, tipo):
        titulo = ""
        conteudo = ""
        id_lista = lista_atual.id

        if tipo == TipoNotificacao.LivroListaLivroAdicionado:
            titulo = "Livro adicionado em lista"
            conteudo = f"{usuario_contexto.nome} adicionou o livro '{livro.titulo}' na lista '{lista_atual.nome}'."
        elif tipo == TipoNotificacao.LivroListaLivroRemovido:
            titulo = "Livro removido da lista"
            conteudo = f"{usuario_contexto.nome} removeu o livro '{livro.titulo}' da lista '{lista_atual.nome}'."

        for usuario_lista_seguir in db.session.query(ListaSeguir).filter_by(usuario_seguindo_id=usuario_contexto.id, lista_id=lista_atual.id).all():
            usuario_notificar = db.session.query(Usuario).filter_by(id=usuario_lista_seguir.usuario_seguidor_id).first()
            
            if usuario_notificar is None:
                continue

            usuario_lista_mover = None
            if lista_nova is not None:
                usuario_lista_mover = db.session.query(ListaSeguir).filter_by(usuario_seguidor_id=usuario_notificar.id, usuario_seguindo_id=usuario_contexto.id, lista_id=lista_nova.id).first()
                if usuario_lista_mover is not None:
                    titulo = "Livro movido para lista"
                    conteudo = f"{usuario_contexto.nome} moveu o livro '{livro.titulo}' para a lista '{lista_nova.nome}'."
                    tipo = TipoNotificacao.LivroListaLivroMovido
                    id_lista = lista_nova.id
                else:
                    titulo = "Livro removido da lista"
                    conteudo = f"{usuario_contexto.nome} removeu o livro '{livro.titulo}' da lista '{lista_atual.nome}'."
                    tipo = TipoNotificacao.LivroListaLivroRemovido
            
            if usuario_notificar.notificacoes and usuario_notificar.notificar_lista_seguindo and usuario_notificar.senha != "":
                link = f"usuario?id={usuario_contexto.id}&idLista={id_lista}&idLivro={livro.id}"
                notificacao_banco = Notificacao.query.filter_by(usuario_id=usuario_notificar.id, tipo=tipo, link=link).order_by(Notificacao.data_gravacao.desc()).first()
                if notificacao_banco is None:
                    notificacao = Notificacao(
                        usuario_id = usuario_notificar.id,
                        usuario_interagiu_id = usuario_contexto.id,
                        titulo = titulo,
                        conteudo = conteudo,
                        img = usuario_contexto.img,
                        tipo = tipo,
                        link = link,
                        obj_id = id_lista
                    )
                    db.session.add(notificacao)


class ListaSeguir(db.Model):
    __tablename__ = 'lista_seguir'
    id = db.Column(db.Integer, primary_key=True)
    usuario_seguidor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # eu usuario
    usuario_seguindo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # estou seguindo a lista de outro usuario
    lista_id = db.Column(db.Integer, db.ForeignKey('lista_livro.id'))
    data_gravacao = db.Column(db.DateTime, default=datetime.now)


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

    livro.titulo = formatar_titulo_livro(livro.titulo)
    livro.titulo_aux = "|" + unidecode(livro.titulo.lower().replace(" ", "")) + "|"
    livro_banco = db.session.query(Livro).filter(Livro.titulo_aux.like(f"%{livro.titulo_aux}%")).first()

    if livro.autor is not None and livro.autor.nome.strip() != "":
        if isinstance(livro.autor, str):
            livro.autor = retornar_usuario(livro.autor, TipoUsuario.Autor)
        elif livro.autor is not None:
            livro.autor.nome_aux = "|" + unidecode(livro.autor.nome.lower().replace(" ", "")) + "|"

    if livro.editora is not None and livro.editora.nome.strip() != "":
        if isinstance(livro.editora, str):
            livro.editora = retornar_usuario(livro.editora, TipoUsuario.Editora)
        else:
            livro.editora.nome_aux = "|" + unidecode(livro.editora.nome.lower().replace(" ", "")) + "|"

    alterar = False

    autor_banco = None
    if livro_banco is not None and livro_banco.autor is not None:
        autor_banco = livro_banco.autor
    elif livro.autor is not None and livro.autor.nome.strip() != "":
        autor_banco = db.session.query(Usuario).filter(
            or_(
                Usuario.nome_aux.like(f"%{livro.autor.nome_aux}%"),
                Usuario.nome_alternativo.like(f"%{livro.autor.nome_aux}%")
            ), Usuario.tipo == TipoUsuario.Autor
        ).first()
    
    if autor_banco is None:
        if livro.autor is not None and livro.autor.nome.strip() != "":
            db.session.add(livro.autor)
            db.session.flush()
            livro.autor.atualizar_caminho_imagem(livro.autor.img, 'templates\\static\\imagens\\usuarios')
            alterar = True
    else:
        if autor_banco.img == "" and livro.autor.img != "":
            autor_banco.atualizar_caminho_imagem(livro.autor.img, 'templates\\static\\imagens\\usuarios')
            alterar = True
        livro.autor = autor_banco

    if livro.editora is not None and livro.editora.nome.strip() != "":
        editora_banco = db.session.query(Usuario).filter(Usuario.nome_aux.like(f"%{livro.editora.nome_aux}%"), Usuario.tipo==TipoUsuario.Editora).first()
        if editora_banco is None:
            db.session.add(livro.editora)
            alterar = True
        else:
            livro.editora = editora_banco

    if livro_banco is None:
        livro.titulo_aux = "|" + unidecode(livro.titulo.lower().replace(" ", "")) + "|"
        db.session.add(livro)
        livro.atualizar_caminho_imagem(livro.img)
        db.session.flush()
        alterar = True
    else:
        livro.id = livro_banco.id
        if livro_banco.autor_id is None:
            livro_banco.autor = livro.autor
            alterar = True
        if livro_banco.editora_id is None:
            livro_banco.editora = livro.editora
            alterar = True
        if livro_banco.img == "" and livro.img != "":
            livro_banco.atualizar_caminho_imagem(livro.img)
            alterar = True
        if livro_banco.descricao == "" and livro.descricao != "":
            livro_banco.descricao = livro.descricao
            alterar = True
        if (livro_banco.data_publicacao is None or livro_banco.data_publicacao == datetime.min) and livro.data_publicacao is not None and livro.data_publicacao != datetime.min:
            livro_banco.data_publicacao = livro.data_publicacao
            alterar = True

    if hasattr(livro, 'site_link') and hasattr(livro, 'link'):
        livro_link = controle_livro_link(livro.id, livro.site_link, livro.link)
        if livro_link is not None and hasattr(livro, 'preco') and livro.preco and livro.preco.strip() != "":
            alterar = alterar or controle_livro_preco(livro.id, livro_link.id, livro.preco)
    
    #if alterar:
        #db.session.commit()


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

    usuario.nome_aux = "|" + unidecode(usuario.nome.lower().replace(" ", "")) + "|"

    usuario_banco = db.session.query(Usuario).filter(Usuario.nome_aux.like(f"%{usuario.nome_aux}%"), Usuario.tipo==tipo).first()

    if usuario_banco is not None:
        return usuario_banco

    return usuario


@event.listens_for(Livro, 'load')
def receive_load(livro, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            livro.procurar_livro_salvo(current_user)
    except Exception:
        pass


@event.listens_for(Usuario, 'after_insert')
def inserir_lista_livros_estaticos(mapper, connection, target):
    if target.tipo != TipoUsuario.Leitor:
        return
    
    connection.execute(
        ListaLivro.__table__.insert(),
        [
            {"usuario_id": target.id, "nome": "Já lidos", "descricao": "Livros que já li"},
            {"usuario_id": target.id, "nome": "Desejo ler", "descricao": "Livros que um dia quero ler"},
            {"usuario_id": target.id, "nome": "Estou lendo", "descricao": "Livros que estou lendo"},
            {"usuario_id": target.id, "nome": "Adquiridos", "descricao": "Meus Livros"},
        ]
    )


@event.listens_for(ListaLivroLivro, 'after_insert')
def inserir_livro_lista_livro_estatico(mapper, connection, target):
    pass


@event.listens_for(ListaLivroLivro, 'after_delete')
def inserir_livro_lista_livro_estatico(mapper, connection, target):
    pass


@event.listens_for(ListaLivro, 'load')
def receive_load(lista_livro, context):
    try:
        from flask_login import current_user
        # Só tenta atualizar se houver contexto de request (evita erro em scripts, shell, etc)
        from flask import has_request_context
        if has_request_context():
            lista_livro.atualizar_status_seguimento(current_user)
    except Exception:
        pass


import sqlite3
from python.imagem import gravar_imagem
def garvar_livros_aux():
    with sqlite3.connect('G:\\Meu Drive\\Python\\Livros\\livros.db') as conexao:
        cursor = conexao.cursor()

        cursor.execute("select nome, img, dataLancamento, descricao, autor, editora from livros;")

        for livro in cursor.fetchall():
            nome = formatar_titulo_livro(livro[0])

            caminho_img = gravar_imagem(nome, livro[1], 'templates\\static\\imagens\\livros', transformar='livro')
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


nomes_livros = """
Crepúsculo
Lua nova
P.S Eu te amo
Andanças
Para todos os garotos que já amei
Agora e para sempre, Lara Jesh
P.S.: Ainda amo você
Crônicas de Avonlea
Mais Crônicas de Avonlea
Os poemas de Blythes
Os contos dos Blythes Vol.1
Os contos dos Blythes Vol.2
Senhora
O caçador de Crocodilos
Muito mais que 5inco minutos
elite
Herdeira
O mar de monstros
O Ladrão de raios
Precisava de você
Nada disso é pra você
fala de amor pra mim
A poesia que trasnforma
Will e Will
O quatrilho
Os causos do guri de uruguaiana
Um de nós está mentindo
De gênio e louco todo mundo tem um pouco
Poderosa 3
Iracema
Cinco Minutos
A viuvinha
Gabriela Cravo e Canela
Destino Nova York
A rainha está morta
Fazer o bem
Diário de um Banana 1
Diário de um Banana 2: Rodick é o cara
Diário de um Banana 3: A gota d' água
Diário de um Banana 4: Dias de cão
Diário de um Banana 5: A verdade nua e crua
Diário de um Banana 6: Casa dos horrores
Diário de um Banana 7: Segurando vela
Diário de um Banana 8: Maré de azar
Diário de um Banana 9: Caindo na estrada
Diário de um Banana 10: Bons tempos
Diário de um Banana 11: Vai ou racha
Diário de um Banana 12: Apertem os cintos
Diário de um Banana 13: Batalha Neval
Diário de um Banana 14: Quebra Tudo
Diário de um Banana 15: Vai Fundo
Diário de um Banana 16: Bola Fora
Diário de um Banana 17: Fräwda Megaxeia
Diário de um Banana 18: Cabeça-oca
Diário de um Banana 19: Baita lambança
A viagem de Gulliver
A gerra do tênis nas ondas do rádio
Liderando para a Felicidade
Umbanda: Um encontro da diversidade racial-uma instituição a serviço do bem
O diário de anne frank
Três
dezoito 
A única coisa
"""
nomes_livros = """
O vendedor de Sonhos 2
"""
nomes_livros = nomes_livros.split("\n")
def gravar_livros_aux2():
    print(nomes_livros)
    from python.crawler import procurar_livros_internet
    for nome_livro in nomes_livros:
        if nome_livro.strip() == "":
            continue
        nome_livro = formatar_titulo_livro(nome_livro)
        print(nome_livro)
        livros = procurar_livros_internet(nome_livro,1)
        if len(livros) == 0:
             continue
        livro = livros[0]
        print(livro.__dict__)
        gravar_livro(livro)
        print('lllggg', livro.__dict__)
        print("gravado com sucesso")


def gravar_imagem_autor(url, nome_autor):
    import io
    import requests
    from python.imagem import processar_imagem, imagem_to_base64
    requests_session = requests.Session()
    
    if url.startswith('<img src'):
        img = url.strip().lstrip('<img src="').rstrip('">')
    elif url.startswith("data:image"):
        img = url
    else:
        response_img = requests_session.get(url)
        if response_img.status_code != 200:
            print("response ruim")
    
        img = Image.open(io.BytesIO(response_img.content))
    
    autor_banco = db.session.query(Usuario).filter(
        or_(
            Usuario.nome == nome_autor,
            Usuario.nome_alternativo.like(f"%{nome_autor}%")
        ), Usuario.tipo == TipoUsuario.Editora
    ).first()

    print('autor_banco', autor_banco)

    if autor_banco is None:
        return
    
    autor_banco.atualizar_caminho_imagem(img, 'templates\\static\\imagens\\usuarios')

    db.session.commit()
        
        
