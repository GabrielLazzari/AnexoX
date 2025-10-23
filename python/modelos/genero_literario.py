from sqlalchemy import Enum as SAEnum, event
from unidecode import unidecode

from python.banco import db


class GeneroLiterario(db.Model):
    __tablename__ = 'genero_literario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="")
    descricao = db.Column(db.String(500), nullable=True, default="")
    icone = db.Column(db.String(256), nullable=True, default="")

    def dicionario(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'nomeCampo': "check" + unidecode(self.nome.capitalize().replace(" ", "").replace("/", "")),
            'descricao': self.descricao,
            'icone': self.icone
        }


class PreferenciasLiterariasUsuario(db.Model):
    __tablename__ = 'preferencia_literaria_usuario'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    id_genero_literario = db.Column(db.Integer, db.ForeignKey('genero_literario.id'))


class EstilosLiterariosLivro(db.Model):
    __tablename__ = 'estilo_literario_livro'
    id = db.Column(db.Integer, primary_key=True)
    id_livro = db.Column(db.Integer, db.ForeignKey('livro.id'))
    id_genero_literario = db.Column(db.Integer, db.ForeignKey('genero_literario.id'))


@event.listens_for(GeneroLiterario.__table__, 'after_create')
def inserir_generos_literarios_estaticos(target, connection, **kw):
    connection.execute(
        GeneroLiterario.__table__.insert(),
        [
            {"nome": "Romance", "descricao": "", "icone": "static\\icones\\heart-outline.svg"},
            {"nome": "Suspense", "descricao": "", "icone": ""},
            {"nome": "Mistério", "descricao": "", "icone": "static\\icones\\footsteps-outline.svg"},
            {"nome": "Aventura", "descricao": "", "icone": ""},
            {"nome": "Policial", "descricao": "", "icone": ""},
            {"nome": "Ficção Científica", "descricao": "", "icone": ""},
            {"nome": "Fantasia", "descricao": "", "icone": ""},
            {"nome": "Técnicos / Estudos", "descricao": "", "icone": ""},
            {"nome": "Bibliográficos / Auto Bibliográficos", "descricao": "", "icone": ""},
            {"nome": "Terror", "descricao": "", "icone": ""},
            {"nome": "Auto Ajuda", "descricao": "", "icone": ""},
            {"nome": "Religioso", "descricao": "", "icone": ""},
            {"nome": "Finanças", "descricao": "", "icone": "static\\icones\\cash-outline.svg"},
            {"nome": "Literatura", "descricao": "", "icone": ""},
            {"nome": "Infanto Juvenil", "descricao": "", "icone": ""},
            {"nome": "Contos", "descricao": "", "icone": ""},
            {"nome": "Poesia", "descricao": "", "icone": ""},
            {"nome": "Histórico", "descricao": "", "icone": ""},
            {"nome": "Ficção", "descricao": "", "icone": ""},
            {"nome": "Drama", "descricao": "", "icone": ""},
            {"nome": "Comédia", "descricao": "", "icone": ""},
        ]
    )