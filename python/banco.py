from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


db = SQLAlchemy()


def criar_registros_estaticos():
    criar_generos_literario()


def criar_generos_literario():
    with db.engine.connect() as conexao:

        '''resultado = conexao.execute(text("""
            SELECT count(*) FROM sqlite_master WHERE type='table' AND name='genero_literario';
        """)).fetchone()

        if True if len(resultado) > 0 and resultado[0] == 1 else False:
            return

        conexao.execute(text("""
            CREATE TABLE IF NOT EXISTS genero_literario (
                id integer NOT NULL,
                descricao varchar(100) NOT NULL,
                PRIMARY KEY (id)
            );
        """))'''

        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Romance');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Suspense');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Mistério');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Aventura');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Policial');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Ficção Científica');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Fantasia');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Técnicos / Estudos');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Bibliográficos / Auto Bibliográficos');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Terror');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Histórico');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Auto Ajuda');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Religioso');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Finanças');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Literatura');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Infanto Juvenil');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Contos');"""))
        conexao.execute(text("""INSERT INTO genero_literario VALUES (null, 'Poesia');"""))

        conexao.commit()


def criar_generos_literario2():
    descricoes = ['Romance', 'Suspense', 'Mistério', 'Aventura', 'Policial', 'Ficção Científica', 'Fantasia',
            'Técnicos / Estudos', 'Bibliográficos / Auto Bibliográficos', 'Terror', 'Histórico',
            'Auto Ajuda', 'Religioso', 'Finanças', 'Literatura', 'Infanto Juvenil', 'Contos', 'Poesia']

    for desc in descricoes:
        existe = GeneroLiterario.query.filter_by(descricao=desc).first()
        if not existe:
            db.session.add(GeneroLiterario(descricao=desc))
    db.session.commit()