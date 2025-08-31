from sqlalchemy import Enum as SAEnum, event

from python.banco import db


class GeneroLiterario(db.Model):
    __tablename__ = 'genero_literario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    icone = db.Column(db.String(256), nullable=True, default="")


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