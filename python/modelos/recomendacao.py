from datetime import datetime

#from sklearn.svm import LinearSVC
#from sklearn.model_selection import train_test_split

from python.banco import db
#from python.modelos.livro import Livro


class LivrosEmAlta(db.Model):
    __tablename__ = 'r_livros_em_alta'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    livro = db.relationship('Livro', foreign_keys=[livro_id])
    clicado = db.Column(db.Boolean, default=False)
    adicionado = db.Column(db.Integer, default=0)
    reagido = db.Column(db.Boolean, default=False)
    comentado = db.Column(db.Integer, default=0)
    data_criado = db.Column(db.DateTime, default=datetime.now)
    data_alterado = db.Column(db.DateTime, default=datetime.now)


class LivrosRecomendados(db.Model):
    __tablename__ = 'r_livros_recomendados'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    livro = db.relationship('Livro', foreign_keys=[livro_id])
    data_criado = db.Column(db.DateTime, default=datetime.now)


class LivrosModeloRecomendacao(db.Model):
    __tablename__ = 'r_livros_modelo_recomendacao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    data_criado = db.Column(db.DateTime, default=datetime.now)


class PessoasEmAlta(db.Model):
    __tablename__ = 'r_pessoas_em_alta'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    pessoa_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    pessoa = db.relationship('Usuario', foreign_keys=[pessoa_id])
    clicado = db.Column(db.Boolean, default=False)
    seguindo = db.Column(db.Boolean, default=False)
    data_criado = db.Column(db.DateTime, default=datetime.now)
    data_alterado = db.Column(db.DateTime, default=datetime.now)


class HistoricoPesquisa(db.Model):
    __tablename__ = 'r_historico_pesquisa'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    pesquisa = db.Column(db.String(1000), nullable=True, default="")
    data_criado = db.Column(db.DateTime, default=datetime.now)

    def dicionario(self):
        return {
            'pesquisa': self.pesquisa
        }


def alterar_livro_em_alta(usuario_id, livro_id, clicado=None, adicionado=None, reagido=None, comentado=None):
    if clicado is None and adicionado is None and reagido is None and comentado is None:
        return

    livro = LivrosEmAlta.query.filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
    if not livro:
        if (adicionado is not None and not adicionado) and (comentado is not None and not comentado):
            return
        
        livro = LivrosEmAlta(
            usuario_id = usuario_id,
            livro_id = livro_id,
            clicado = False,
            adicionado = 0,
            reagido = False,
            comentado = 0
        )

        db.session.add(livro)
    else:
        livro.data_alterado = datetime.now()

    if clicado is not None:
        livro.clicado = clicado
        db.session.commit()

    if adicionado is not None:
        if livro.adicionado is None:
            livro.adicionado = 0
        livro.adicionado += 1 if adicionado else -1
        if livro.adicionado < 0:
            livro.adicionado = 0

    if reagido is not None:
        livro.reagido = reagido
        db.session.commit()

    if comentado is not None:
        if livro.comentado is None:
            livro.comentado = 0
        livro.comentado += 1 if comentado else -1
        if livro.comentado < 0:
            livro.comentado = 0


def alterar_pessoa_em_alta(usuario_id, pessoa_id, clicado=None, seguindo=None):
    if clicado is None and seguindo is None:
        return

    pessoa = PessoasEmAlta.query.filter_by(usuario_id=usuario_id, pessoa_id=pessoa_id).first()
    if not pessoa:
        if seguindo is not None and not seguindo:
            return

        pessoa = PessoasEmAlta(
            usuario_id = usuario_id,
            pessoa_id = pessoa_id
        )

        db.session.add(pessoa)
    else:
        pessoa.data_alterado = datetime.now()

    if clicado is not None:
        pessoa.clicado = clicado
        db.session.commit()

    if seguindo is not None:
        pessoa.seguindo = seguindo


def adicionar_historico_pesquisa(usuario_id, pesquisa):
    ultimo = HistoricoPesquisa.query.filter_by(usuario_id=usuario_id).order_by(HistoricoPesquisa.data_criado.desc()).first()
    if ultimo and ultimo.pesquisa == pesquisa:
        return
    
    db.session.add(HistoricoPesquisa(
        usuario_id = usuario_id,
        pesquisa = pesquisa[:1000]
    ))

    db.session.commit()


def calcular_recomendacao_livro():
    gerar_recomendacao = False

    if gerar_recomendacao:
        pass


def gerar_modelo_recomendacao():
    
    for livo in db.session.query(Livro).filter_by().all():
        pass

    pass