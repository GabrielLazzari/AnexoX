
from python.crawler import procurar_livros_internet
from python.modelos.usuario import *
from python.modelos.livro import *
from python.modelos.publicacao import *


def processar_filtros(filtros, retornar_quantidade=False):
    #.limit(10)  # pega 10 registros
    #.offset(20)  # pulando os primeiros 20

    filtros['campoPesquisa'] = filtros.get('campoPesquisa', '').strip()
    filtros['id_usuario'] = filtros.get('id_usuario', '0')
    filtros['limit'] = filtros.get('limit', '20')
    filtros['skip'] = filtros.get('skip', '0')

    if filtros.get('checkLivros', False):

        condicao = []
        if filtros['campoPesquisa'] != "":
            print(filtros['campoPesquisa'])
            condicao.append(Livro.titulo.ilike(f"%{filtros['campoPesquisa']}%"))

        if retornar_quantidade:
            return Livro.query.filter(*condicao).count()

        ordenacao = []
        if filtros.get('checkOrdenarDatapublicacao', False):
            ordenacao = [Livro.data_publicacao.desc()]
        elif filtros.get('checkOrdenarTitulo', False):
            ordenacao = [Livro.descricao.desc()]
        elif filtros.get('checkOrdenarAutor', False):
            ordenacao = [Livro.autor.nome.desc()]
        elif filtros.get('checkOrdenarEditora', False):
            ordenacao = [Livro.editora.nome.desc()]

        livros = Livro.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

        if len(livros) == 0 and len(filtros['campoPesquisa']) >= 3:
            print('aqui')
            livros = procurar_livros_internet(filtros['campoPesquisa'])

        print('l', livros)

        return livros

    elif filtros.get('checkLeitores', False) or filtros.get('checkAutores', False) or filtros.get('checkEditoras', False):

        condicao = []
        if filtros['campoPesquisa'] != "":
            condicao.append(Usuario.nome.ilike(f"%{filtros['campoPesquisa']}%"))
        if filtros.get('checkLeitores', False):
            condicao.append(Usuario.tipo == TipoUsuario.Leitor)
        elif filtros.get('checkAutores', False):
            condicao.append(Usuario.tipo == TipoUsuario.Autor)
        elif filtros.get('checkEditoras', False):
            condicao.append(Usuario.tipo == TipoUsuario.Editora)

        print('condicao', condicao)

        if retornar_quantidade:
            return Usuario.query.filter(*condicao).count()

        ordenacao = []
        if filtros.get('checkOrdenarDatapublicacao', False):
            ordenacao = [Usuario.data_cadastro.desc()]
        elif filtros.get('checkOrdenarTitulo', False):
            ordenacao = [Usuario.nome.desc()]

        print('ordenacao', ordenacao)

        return Usuario.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

    elif filtros.get('checkPublicacoes', False):
        condicao = []

        if filtros['campoPesquisa'] != "":
            condicao.append(Publicacao.titulo.ilike(f"%{filtros['campoPesquisa']}%"))

        if retornar_quantidade:
            return Publicacao.query.filter(*condicao).count()

        ordenacao = []
        return Publicacao.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

    return []



'''import difflib

from unidecode import unidecode

from python.crawler import procurar_livros_internet


# python string predictions


def nomes_proximos(pesquisa, lista):
    return difflib.get_close_matches(
        unidecode(pesquisa.lower().casefold()),
        list(lista.keys()), n=10, cutoff=0.3
    )


def livros_proximos(pesquisa):
    titulo_livros = retornar_titulos_livros()
    titulo_livros_processados = {unidecode(titulo.lower().casefold()): [titulo] for titulo in titulo_livros}
    print(titulo_livros_processados)
    titulo_livros = nomes_proximos(pesquisa, titulo_livros_processados)
    titulo_livros = [item for nome in titulo_livros for item in titulo_livros_processados[nome]]

    return titulo_livros


def usuarios_proximos(pesquisa):
    nome_usuarios = retornar_nomes_usuarios()
    nome_usuarios_processados = {unidecode(nome.lower().casefold()): [nome] for nome in nome_usuarios}
    nome_usuarios = nomes_proximos(pesquisa, nome_usuarios_processados)
    nome_usuarios = [item for nome in nome_usuarios for item in nome_usuarios_processados[nome]]

    return nome_usuarios


def sugestoes_pesquisa(pesquisa, filtros={}, resumido=True):
    titulo_livros = livros_proximos(pesquisa)
    nome_usuarios = usuarios_proximos(pesquisa)

    livros = retonar_livros(titulo_livros, resumido=resumido)
    usuarios = retonar_usuarios(nome_usuarios, resumido=resumido)

    pesquisa = titulo_livros + nome_usuarios

    #if len(livros) == 0 and len(pesquisa) > 3:
    #    livros = procurar_livros_internet(pesquisa)

    qtd_pesquisa = 5
    if len(livros) == 0 or len(usuarios) == 0:
        qtd_pesquisa = 8
    elif len(livros) == 0 and len(usuarios) == 0:
        qtd_pesquisa = 10

    pesquisa = pesquisa[:qtd_pesquisa]

    return {
        'pesquisa': pesquisa,
        'livros': livros,
        'usuarios': usuarios
    }


#print(sugestoes_pesquisa("qatro"))'''




