import uuid

from flask import session
from flask_login import current_user
from unidecode import unidecode
from werkzeug.utils import secure_filename

from python.cache import cache, session_key
from python.crawler import procurar_livros_internet
from python.modelos.recomendacao import *
from python.modelos.usuario import *
from python.modelos.livro import *
from python.modelos.publicacao import *


def processar_filtros(filtros, retornar_quantidade=False):
    #.limit(10)  # pega 10 registros
    #.offset(20)  # pulando os primeiros 20
    
    filtros['campoPesquisa'] = filtros.get('campoPesquisa', '')
    filtros['campoPesquisaBusca'] = unidecode(filtros['campoPesquisa'].strip().lower().replace(" ", ""))
    filtros['id_usuario'] = filtros.get('id_usuario', '0')
    filtros['limit'] = filtros.get('limit', '20')
    filtros['skip'] = filtros.get('skip', '0')

    if filtros.get('checkLivros', False):
        condicao = []
        ids_generos_consultar = retornar_ids_generos_consultar(filtros)

        if filtros['campoPesquisaBusca'] != "":
            condicao.append(Livro.titulo_aux.ilike(f"%{filtros['campoPesquisaBusca']}%"))

        if retornar_quantidade:
            if len(ids_generos_consultar) > 0:
                condicao.append(GeneroLiterario.id.in_(retornar_ids_generos_consultar(filtros)))
                return Livro.query.join(Livro.estilos_literarios).filter(*condicao).count()
            
            return Livro.query.filter(*condicao).count()

        ordenacao = retornar_ordenacao(filtros)

        if len(ids_generos_consultar) > 0:
            condicao.append(GeneroLiterario.id.in_(retornar_ids_generos_consultar(filtros)))
            livros = Livro.query.join(Livro.estilos_literarios).filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()
        else:
            livros = Livro.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

        if len(livros) == 0 and len(filtros['campoPesquisaBusca']) >= 3:

            chave_pesquisa = unidecode(secure_filename(filtros['campoPesquisa'].replace(" ", "")))
            
            procurar_novos_livros = True
            livros_cache_encontrados = cache.get(session_key('livro_cache'))

            if livros_cache_encontrados is not None:
                livros = []
                for l, v in livros_cache_encontrados.items():
                    print("lllll", l, chave_pesquisa in l)
                    if chave_pesquisa in l:
                        procurar_novos_livros = False
                        livros.append(v)

            if procurar_novos_livros:
                livros = procurar_livros_internet(filtros['campoPesquisa'])
                livros_cache = {}
                for pos, l in enumerate(livros):
                    titulo_aux = "|" + unidecode(l.titulo.lower().replace(" ", "")) + "|"
                    livro_banco = db.session.query(Livro).filter(or_(Livro.titulo_aux.like(f"%{titulo_aux}%"), Livro.descricao == l.descricao)).first()
                    if livro_banco:
                        livros_cache['cache' + chave_pesquisa + str(pos)] = livro_banco.id
                        livros[pos] = livro_banco
                    else:
                        l.id = 'cache' + chave_pesquisa + str(pos)
                        livros_cache[l.id] = l
                cache.set(session_key('livro_cache'), livros_cache)

            '''
            livros = procurar_livros_internet(filtros['campoPesquisa'])
            livros_cache = {}
            for pos, l in enumerate(livros):
                titulo_aux = "|" + unidecode(l.titulo.lower().replace(" ", "")) + "|"
                livro_banco = db.session.query(Livro).filter(or_(Livro.titulo_aux.like(f"%{titulo_aux}%"), Livro.descricao == l.descricao)).first()
                if livro_banco:
                    livros_cache['cache' + str(pos)] = livro_banco.id
                    livros[pos] = livro_banco
                else:
                    l.id = 'cache' + str(pos)
                    livros_cache[l.id] = l
            cache.set(session_key('livro_cache'), livros_cache)'''
            print(cache)

        return livros

    elif filtros.get('checkLeitores', False) or filtros.get('checkAutores', False) or filtros.get('checkEditoras', False):

        condicao = [Usuario.ativo.is_(True)]
        if filtros['campoPesquisa'] != "":
            condicao.append(Usuario.nome_aux.ilike(f"%{filtros['campoPesquisa']}%"))
        if filtros.get('checkLeitores', False):
            condicao.append(Usuario.tipo == TipoUsuario.Leitor)
        elif filtros.get('checkAutores', False):
            condicao.append(Usuario.tipo == TipoUsuario.Autor)
        elif filtros.get('checkEditoras', False):
            condicao.append(Usuario.tipo == TipoUsuario.Editora)

        if retornar_quantidade:
            return Usuario.query.filter(*condicao).count()

        ordenacao = retornar_ordenacao(filtros)

        return Usuario.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

    elif filtros.get('checkPublicacoes', False):
        if current_user.is_authenticated:
            condicao = [Publicacao.usuario_id != current_user.id]
        else:
            condicao = [Publicacao.usuario_id == 0]

        if filtros['campoPesquisa'] != "":
            condicao.append(Publicacao.conteudo.ilike(f"%{filtros['campoPesquisa']}%"))

        if retornar_quantidade:
            return Publicacao.query.filter(*condicao).count()

        ordenacao = retornar_ordenacao(filtros)

        return Publicacao.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()
    
    elif filtros.get('checkNotificacoes', False):
        condicao = [Notificacao.usuario_id == current_user.id]
        if filtros['campoPesquisa'] != "":
            condicao.append(Notificacao.conteudo.ilike(f"%{filtros['campoPesquisa']}%"))

        if retornar_quantidade:
            return Notificacao.query.filter(*condicao).count()
        
        ordenacao = retornar_ordenacao(filtros)

        return Notificacao.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()

    elif filtros.get('tipoSeguindo', '').strip() != "":
        condicao = []
        if (filtros.get("tipoSeguindo") == "seguindo"):
            condicao.append(UsuarioSeguir.usuario_seguidor_id == filtros["idUsuario"])
        else:
            condicao.append(UsuarioSeguir.usuario_seguindo_id == filtros["idUsuario"])

        if filtros['campoPesquisa'] != "":
            condicao.append(Usuario.nome_aux.ilike(f"%{filtros['campoPesquisa']}%"))

        if retornar_quantidade:
            return UsuarioSeguir.query.filter(*condicao).count()
        
        ordenacao = retornar_ordenacao(filtros)

        if filtros['campoPesquisa'] != "":
            if (filtros.get("tipoSeguindo") == "seguindo"):
                usuarios_seguir = UsuarioSeguir.query.join(Usuario, Usuario.id == UsuarioSeguir.usuario_seguidor_id).filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()
            else:
                usuarios_seguir = UsuarioSeguir.query.join(Usuario, Usuario.id == UsuarioSeguir.usuario_seguindo_id).filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()
        else:
            usuarios_seguir = UsuarioSeguir.query.filter(*condicao).order_by(*ordenacao).limit(filtros['limit']).offset(filtros['skip']).all()
        
        if (filtros.get("tipoSeguindo") == "seguindo"):
            return [u.usuario_seguindo for u in usuarios_seguir]
        else:
            return [u.usuario_seguidor for u in usuarios_seguir]

    return []


def retornar_ids_generos_consultar(filtros):
    ids = []

    generos = [g.dicionario() for g in GeneroLiterario.query.filter().all()]
    for genero in generos:
        if filtros.get(genero['nomeCampo'], False):
            ids.append(genero['id'])
    
    return ids


def retornar_ordenacao(filtros):
    ordenacao = []

    if filtros.get('checkLivros', False):
        if filtros.get('checkOrdenarTitulo', False):
            ordenacao = [Livro.titulo_aux.desc()] if filtros.get('checkDecrescente', False) else [Livro.titulo_aux]
        elif filtros.get('checkOrdenarAutor', False):
            ordenacao = [Livro.nome_autor.desc()] if filtros.get('checkDecrescente', False) else [Livro.nome_autor]
        elif filtros.get('checkOrdenarEditora', False):
            ordenacao = [Livro.nome_editora.desc()] if filtros.get('checkDecrescente', False) else [Livro.nome_editora]
        else:
            ordenacao = [Livro.data_publicacao] if filtros.get('checkDecrescente', False) else [Livro.data_publicacao.desc()]

    elif filtros.get('checkLeitores', False) or filtros.get('checkAutores', False) or filtros.get('checkEditoras', False):
        if filtros.get('checkOrdenarTitulo', False) or filtros.get('checkOrdenarAutor', False) or filtros.get('checkOrdenarEditora', False):
            ordenacao = [Usuario.nome_aux.desc()] if filtros.get('checkDecrescente', False) else [Usuario.nome_aux]
        else:
            ordenacao = [Usuario.data_cadastro] if filtros.get('checkDecrescente', False) else [Usuario.data_cadastro.desc()]

    elif filtros.get('checkPublicacoes', False):
        ordenacao = [Publicacao.data_gravacao.desc()]

    elif filtros.get('checkNotificacoes', False):
        ordenacao = [Notificacao.data_gravacao.desc()]

    return ordenacao


def sugestoes_pesquisa(pesquisa, id_usuario=0, limite=3):

    pesquisa = unidecode(pesquisa.strip().lower().replace(" ", ""))

    condicao_pesquisas = []
    if pesquisa != "":
        condicao_pesquisas.append(HistoricoPesquisa.pesquisa.ilike(f"%{pesquisa}%"))
    if id_usuario != 0:
        condicao_pesquisas.append(HistoricoPesquisa.usuario_id == id_usuario)

    livros = sugestao_pesquisa_livros(pesquisa, id_usuario, limite)
    usuarios = [] if id_usuario == 0 else sugestao_pesquisa_usuarios(pesquisa, id_usuario, limite)

    limite_pesquisa = 10
    if len(livros) > 0:
        limite_pesquisa -= 3
    if len(usuarios) > 0:
        limite_pesquisa -= 3

    pesquisas = []
    for pesquisa in HistoricoPesquisa.query.filter(*condicao_pesquisas).order_by(HistoricoPesquisa.data_criado.desc()).distinct(HistoricoPesquisa.pesquisa).limit(limite_pesquisa).all():
        if not any(pesquisa.pesquisa == p.pesquisa for p in pesquisas):
            pesquisas.append(pesquisa)

    dados = {
        'pesquisas': [pesquisa.dicionario() for pesquisa in pesquisas],
        'livros': [livro.dicionario() for livro in livros],
        'usuarios': [usuario.dicionario() for usuario in usuarios]
    }

    return dados


def sugestao_pesquisa_livros(pesquisa="", id_usuario=0, limite=12):
    condicao_livros = []

    if id_usuario != 0:
        if limite == 3:
            condicao_livros.append(LivrosEmAlta.usuario_id == id_usuario)
        else:
            condicao_livros.append(LivrosEmAlta.usuario_id != id_usuario)

    if pesquisa == "":
        livros = []
        for livro in LivrosEmAlta.query.filter(*condicao_livros).order_by(LivrosEmAlta.data_alterado.desc()).distinct(LivrosEmAlta.livro_id).limit(limite).all():
            if not any(livro.livro.id == livro_alta.id for livro_alta in livros):
                livros.append(livro.livro)
        
        if len(livros) <= limite:
            for livro in LivrosEmAlta.query.filter().order_by(LivrosEmAlta.data_alterado.desc()).limit(limite - len(livros)).all():
                if not any(livro.livro.id == livro_alta.id for livro_alta in livros):
                    livros.append(livro.livro)

        if len(livros) <= limite:
            for livro in Livro.query.filter().order_by(Livro.data_gravacao.desc()).limit(limite - len(livros)).all():
                if not any(livro.id == livro_alta.id for livro_alta in livros):
                    livros.append(livro)

    else:
        livros = Livro.query.filter(Livro.titulo_aux.ilike(f"%{pesquisa}%")).order_by(Livro.titulo.desc()).limit(limite).all()

    return livros


def sugestao_pesquisa_usuarios(pesquisa, id_usuario=0, limite=3):
    condicao_usuarios = []

    if id_usuario != 0:
        condicao_usuarios.append(PessoasEmAlta.usuario_id == id_usuario)

    if pesquisa == "":
        usuarios = []
        for pessoa in PessoasEmAlta.query.filter(*condicao_usuarios).order_by(PessoasEmAlta.data_alterado.desc()).limit(limite).all():
            if not any(usuario.id == pessoa.pessoa.id for usuario in usuarios):
                if pessoa.pessoa.ativo:
                    usuarios.append(pessoa.pessoa)
        
        if len(usuarios) <= limite:
            for pessoa in PessoasEmAlta.query.filter().order_by(PessoasEmAlta.data_alterado.desc()).limit(limite - len(usuarios)).all():
                if not any(usuario.id == pessoa.pessoa.id for usuario in usuarios):
                    if pessoa.pessoa.ativo:
                        usuarios.append(pessoa.pessoa)

        if len(usuarios) <= limite:
            for usuario in Usuario.query.filter(Usuario.ativo.is_(True)).order_by(Usuario.data_cadastro.desc()).limit(limite - len(usuarios)).all():
                if not any(usuario_aux.id == usuario.id for usuario_aux in usuarios):
                    usuarios.append(usuario)

    else:
        usuarios = Usuario.query.filter(Usuario.ativo.is_(True), Usuario.nome_aux.ilike(f"%{pesquisa}%")).order_by(Usuario.nome.desc()).limit(3).all()

    return usuarios


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




