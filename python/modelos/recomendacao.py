from datetime import datetime

from python.banco import db
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix


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
    divulgado = db.Column(db.Integer, default=0)
    data_criado = db.Column(db.DateTime, default=datetime.now)
    data_alterado = db.Column(db.DateTime, default=datetime.now)
    data_divulgado = db.Column(db.DateTime, default=datetime.min)


class LivroRecomendado(db.Model):
    __tablename__ = 'r_livros_recomendados'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    livro = db.relationship('Livro', foreign_keys=[livro_id])
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


def alterar_livro_em_alta(usuario_id, livro_id, clicado=None, adicionado=None, reagido=None, comentado=None, divulgado=None):
    if clicado is None and adicionado is None and reagido is None and comentado is None and divulgado is None:
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
            comentado = 0,
            divulgado = 0
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

    if divulgado is not None:
        if livro.divulgado is None:
            livro.divulgado = 0
        livro.divulgado += 1 #if divulgado else -1
        livro.data_divulgado = datetime.now()
        if livro.divulgado < 0:
            livro.divulgado = 0


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


def calcular_recomendacao_livro(usuario_id):
    from python.modelos.notificacao import Notificacao, TipoNotificacao

    modelo, user_map, livro_map = RecomendadorLivros.gerar_modelo()

    livros_sugeridos = RecomendadorLivros.recomendar_livros(usuario_id, modelo, user_map, livro_map)

    notificar = False
    for livro in livros_sugeridos:
        livro_recomendado_gravado = LivroRecomendado.query.filter_by(usuario_id=usuario_id, livro_id=livro.id).first()
        if livro_recomendado_gravado is None:
            if not notificar:
                notificacao = Notificacao(
                    usuario_id = usuario_id,
                    usuario_interagiu_id = usuario_id,
                    titulo = "Sugestão de Livro",
                    conteudo = livro.titulo,
                    img = livro.img,
                    tipo = TipoNotificacao.SugestaoLivro,
                    link = "livro?id=" + str(livro.id),
                    obj_id = livro.id
                )
                db.session.add(notificacao)

                livro_recomendado = LivroRecomendado(
                    usuario_id = usuario_id,
                    livro_id = livro.id
                )
                db.session.add(livro_recomendado)

                db.session.commit()

            notificar = True

    return notificar


class RecomendadorLivros:
    @staticmethod
    def gerar_modelo():
        from python.modelos.livro import Livro
        from python.modelos.usuario import Usuario, UsuarioSeguir
        """
        Extrai dados das tabelas e treina um modelo de recomendação
        baseado em similaridade de usuários.
        Retorna o modelo treinado e os mapeamentos auxiliares.
        """
        # === 1. Extrair interações ===
        interacoes = db.session.query(
            LivrosEmAlta.usuario_id,
            LivrosEmAlta.livro_id,
            LivrosEmAlta.clicado,
            LivrosEmAlta.adicionado,
            LivrosEmAlta.reagido,
            LivrosEmAlta.comentado
        ).all()

        if not interacoes:
            print("Nenhuma interação encontrada.")
            return None, None, None

        df = pd.DataFrame(interacoes, columns=[
            'usuario_id', 'livro_id', 'clicado', 'adicionado', 'reagido', 'comentado'
        ])

        df = df.fillna(0)

        # === 2. Calcular score implícito ===
        # pondera o quanto cada ação significa interesse
        df['score'] = (
            df['clicado'].astype(int) * 1 +
            df['adicionado'].astype(int) * 3 +
            df['reagido'].astype(int) * 2 +
            df['comentado'].astype(int)
        )

        # === 3. Reforçar score por influência dos amigos ===
        seguir = db.session.query(UsuarioSeguir).all()
        amigos = {}
        for s in seguir:
            amigos.setdefault(s.usuario_seguidor_id, []).append(s.usuario_seguindo_id)

        for uid in df['usuario_id'].unique():
            if uid in amigos:
                livros_amigos = df[df['usuario_id'].isin(amigos[uid])]['livro_id']
                df.loc[df['livro_id'].isin(livros_amigos) & (df['usuario_id'] == uid), 'score'] += 1

        # === 4. Criar matriz usuário × livro ===
        user_ids = df['usuario_id'].unique()
        livro_ids = df['livro_id'].unique()
        user_map = {u: i for i, u in enumerate(user_ids)}
        livro_map = {l: i for i, l in enumerate(livro_ids)}

        df['user_idx'] = df['usuario_id'].map(user_map)
        df['livro_idx'] = df['livro_id'].map(livro_map)

        matriz = csr_matrix(
            (df['score'], (df['user_idx'], df['livro_idx'])),
            shape=(len(user_ids), len(livro_ids))
        )

        # === 5. Treinar modelo SVD ===
        modelo = TruncatedSVD(n_components=20, random_state=42)
        modelo.fit(matriz)

        return modelo, user_map, livro_map

    @staticmethod
    def recomendar_livros(usuario_id, modelo, user_map, livro_map, top_n=5):
        from python.modelos.livro import Livro
        from python.modelos.usuario import Usuario, UsuarioSeguir
        """
        Retorna uma lista de livros recomendados para o usuário informado.
        """
        if modelo is None:
            print("Modelo não treinado.")
            return []

        # === 1. Inverter mapeamentos ===
        inv_user_map = {v: k for k, v in user_map.items()}
        inv_livro_map = {v: k for k, v in livro_map.items()}

        # === 2. Recriar matriz de interações ===
        interacoes = db.session.query(
            LivrosEmAlta.usuario_id,
            LivrosEmAlta.livro_id,
            LivrosEmAlta.clicado,
            LivrosEmAlta.adicionado,
            LivrosEmAlta.reagido,
            LivrosEmAlta.comentado
        ).all()

        df = pd.DataFrame(interacoes, columns=[
            'usuario_id', 'livro_id', 'clicado', 'adicionado', 'reagido', 'comentado'
        ])

        df = df.fillna(0)

        df['score'] = (
            df['clicado'].astype(int) * 1 +
            df['adicionado'].astype(int) * 3 +
            df['reagido'].astype(int) * 2 +
            df['comentado'].astype(int)
        )
        df['user_idx'] = df['usuario_id'].map(user_map)
        df['livro_idx'] = df['livro_id'].map(livro_map)

        matriz = csr_matrix(
            (df['score'], (df['user_idx'], df['livro_idx'])),
            shape=(len(user_map), len(livro_map))
        )

        # === 3. Vetores latentes ===
        user_latent = modelo.transform(matriz)

        if usuario_id not in user_map:
            print("Usuário não encontrado no modelo.")
            return []

        user_idx = user_map[usuario_id]
        similaridades = cosine_similarity([user_latent[user_idx]], user_latent)[0]
        similares_idx = np.argsort(similaridades)[::-1][1:6]

        # === 4. Buscar livros populares entre os usuários semelhantes ===
        similares_ids = [inv_user_map[i] for i in similares_idx]
        df_similares = df[df['usuario_id'].isin(similares_ids)]

        # Filtra livros que o usuário ainda não interagiu
        livros_usuario = set(df[df['usuario_id'] == usuario_id]['livro_id'])
        candidatos = (
            df_similares[~df_similares['livro_id'].isin(livros_usuario)]
            .groupby('livro_id')['score'].sum()
            .sort_values(ascending=False)
            .head(top_n)
        )

        livros_recomendados = db.session.query(Livro).filter(Livro.id.in_(candidatos.index)).all()

        return livros_recomendados