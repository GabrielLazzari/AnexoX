from datetime import timedelta
import hashlib
import json
import os

from flask import Flask, g, render_template, request, redirect, session, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from sqlalchemy import inspect
from unidecode import unidecode
from werkzeug.utils import secure_filename

from publicacao import publicacao_bp

from python.banco import db
from python.cache import init_cache, cache, session_key
#from python.crawler import finalizar_crawler_drivers
from python.modelos.comentario import *
from python.modelos.usuario import *
from python.modelos.genero_literario import *
from python.modelos.livro import *
from python.modelos.publicacao import *
from python.modelos.reacao import *
from python.modelos.recomendacao import *
from python.modelos.notificacao import *
from python.pesquisa import processar_filtros, sugestoes_pesquisa, sugestao_pesquisa_livros

app = Flask(__name__, static_folder='templates/static')
app.register_blueprint(publicacao_bp)
app.secret_key = 'ola'
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste_sql_alchemy.db'
app.config['UPLOAD_FOLDER'] = 'templates\\static\\imagens\\usuarios'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
init_cache(app)
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()


@lm.user_loader
def user_loader(id):
    return db.session.query(Usuario).filter_by(id=id).first()


def retornar_generos_literario():
    generos = db.session.query(GeneroLiterario).filter_by().all()

    return [g.dicionario() for g in generos]


@app.before_request
def carregar_dados():
    g.generos = retornar_generos_literario()


@app.context_processor
def inject_variavel():
    return dict(generos=g.get("generos", None))


def conexao_commit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise
    return wrapper


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    pagina_solicitada = unidecode(request.args.get("pagina", "usuario").lower())

    print(pagina_solicitada, request.args)

    if request.method == "GET":
        return render_template("login.html", nome="", senha="", **request.args)
    elif request.method == "POST":
        nome = request.form['campoNome']
        senha = request.form['campoSenha']

        usuario = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not usuario:
            return render_template("login.html", erro="Nome ou senha incorretos", nome=nome, senha=senha, **request.args)

        login_user(usuario)
        dic_request = request.args.to_dict()
        if "pagina" in dic_request:
            del dic_request["pagina"]
        print('pagina_solicitada', pagina_solicitada, dic_request)
        return redirect(url_for(pagina_solicitada, **dic_request))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    pagina_solicitada = unidecode(request.args.get("pagina", "usuario").lower())

    if request.method == "GET":
        usuario = Usuario()
        if current_user.is_authenticated:
            usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
        return render_template("cadastro.html", usuario=usuario.dicionario(), editando_usuario=current_user.is_authenticated)

    elif request.method == "POST":
        novo_usuario = Usuario(
            id = current_user.id if current_user.is_authenticated else None,
            nome=request.form['campoNome'],
            senha=request.form['campoSenha'],
            senha_confirmar=request.form['campoConfirmarSenha'],
            email=request.form['campoEmail'],
            cnpj=request.form['campoCnpj'],
            tipo=TipoUsuario(int(request.form['tipoUsuario'])),
            img = request.files.get('imagem', ''),
            preferencias_literarias = request.form.get("campoPreferenciasLiterarias", "").replace(" ", "").split(";")
        )

        if (msg_erro := novo_usuario.gravar()) != "":
            return render_template("cadastro.html", erro=msg_erro, usuario=novo_usuario.dicionario(), editando_usuario=current_user.is_authenticated)

        login_user(novo_usuario)

        return redirect(url_for(pagina_solicitada))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("inicio"))


@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')


@app.route("/retornarGenerosLiterarios", methods=["GET", "POST"])
def retornar_generos_literarios_tela():
    return jsonify(retornar_generos_literario())


def retornar_filtros_vazio(tipoFiltro="livros", livros=False, leitores=False, autores=False, editoras=False):
    tipoFiltro = tipoFiltro.strip()
    if livros or tipoFiltro == "" or "livro" in tipoFiltro:
        livros=True; leitores=False; autores=False; editoras=False
    elif leitores or "leitor" in tipoFiltro:
        livros=False; leitores=True; autores=False; editoras=False
    elif autores or "autor" in tipoFiltro:
        livros=False; leitores=False; autores=True; editoras=False
    elif editoras or "editora" in tipoFiltro:
        livros=False; leitores=False; autores=False; editoras=True

    dic_generos = {v.nomeCampo: False for v in retornar_generos_literario()}

    dic_padrao = {
        "campoPesquisa": "",
        "campoPesquisaBusca": "",
        "checkAutores": autores,
        "checkCrescente": True,
        "checkDecrescente": False,
        "checkEditoras": editoras,
        "checkEmalta": False,
        "checkSugeridos": False,
        "checkLeitores": leitores,
        "checkLivros": livros,
        "checkOrdenarAutor": False,
        "checkOrdenarDatapublicacao": True,
        "checkOrdenarEditora": False,
        "checkOrdenarTitulo": False,
        "checkPublicacoes": False,
        "checkTodosEstilos": False,
        "limit": 20,
        "primeiroretorno": True,
        "skip": 0,
        "paginaAtual": 1
    }

    return dic_generos | dic_padrao


@app.route('/pesquisa', methods=['POST', 'GET'])
def pesquisa():
    filtros = request.form.to_dict()
    if len(filtros) == 0:
        if request.is_json:
            filtros = request.get_json()
        else:
            tipoFiltro = request.args.get('tipoFiltro', 'livros')
            filtros = retornar_filtros_vazio(tipoFiltro=tipoFiltro)
    else:
        for chave, valor in filtros.items():
            if valor.lower() == 'true':
                filtros[chave] = True
            elif valor.lower() == 'false':
                filtros[chave] = False

    if filtros.get('campoPesquisa', '').strip() != "":
        id_usuario = current_user.id if current_user.is_authenticated else 0
        adicionar_historico_pesquisa(id_usuario, filtros.get('campoPesquisa', "").strip())

    if filtros.get('primeiroretorno', True):
        print('Primeiro retorno')
        filtros['qtdItens'] = processar_filtros(filtros, retornar_quantidade=True)
        return render_template('pesquisa.html', filtros=filtros)
    else:
        if not current_user.is_authenticated:
            if filtros['checkLeitores']:
                return jsonify({"erro": "Para acessar os leitores, deve estar logado no sistema"})
            elif filtros['checkAutores']:
                return jsonify({"erro": "Para acessar os autores, deve estar logado no sistema"})
            elif filtros['checkEditoras']:
                return jsonify({"erro": "Para acessar as editoras, deve estar logado no sistema"})
            elif filtros['checkPublicacoes']:
                return jsonify({"erro": "Para acessar as publicações, deve estar logado no sistema"})

        print('Segundo retorno')
        retorno = processar_filtros(filtros)
        retorno = [r.dicionario() for r in retorno]
        #print(retorno)
        return jsonify({'erro': '', 'dados': retorno})


@app.route('/pesquisaLivros', methods=['POST', 'GET'])
def pesquisa_livros():
    filtros = request.get_json()
    filtros['checkLivros'] = True
    print('filtrollll', filtros)
    retorno = processar_filtros(filtros)
    retorno = [r.dicionario() for r in retorno]
    return jsonify({'erro': '', 'dados': retorno})


@app.route('/sugestaoPesquisa', methods=['GET', 'POST'])
def sugestao_pesquisa():
    dados = request.get_json()

    id_usuario = current_user.id if current_user.is_authenticated else 0

    retorno = sugestoes_pesquisa(dados['pesquisa'].strip(), id_usuario)

    return jsonify(retorno)


@app.route('/sugestaoPesquisaLivros', methods=['GET', 'POST'])
def sugestao_pesquisa_livro():
    id_usuario = current_user.id if current_user.is_authenticated else 0
    livros = sugestao_pesquisa_livros(id_usuario=id_usuario)
    return jsonify({ 'livros': [livro.dicionario() for livro in livros] })


@app.route('/usuario', methods=['GET', 'POST'])
def usuario():
    id_usuario = request.args.get('id', '0')
    interacao = request.args.get('interacao', '')
    pagina = None if request.args.get('ignore', None) is not None else "Usuário"

    if not current_user.is_authenticated:
        return redirect(url_for("login", pagina=pagina, id=id_usuario))

    usuario_tela_logado = False

    print('usuario_atual', current_user, 'autenticado:', current_user.is_authenticated, 'anonimo:', current_user.is_anonymous)

    if id_usuario == '0' or (current_user.is_authenticated and int(id_usuario) == current_user.id):

        usuario = current_user
        usuario_tela_logado = True

    else:
        usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
        if not usuario:
            #flash("Usuário não encontrado", "error")
            return redirect(url_for("pesquisa", tipoFiltro='autor'))
        alterar_pessoa_em_alta(current_user.id, usuario.id, clicado=True)

    usuario.usuario_tela_logado = usuario_tela_logado

    return render_template('usuario.html', usuario=usuario.dicionario(usuario_tela_logado=usuario_tela_logado), interacao=interacao)


@app.route('/excluirUsuario', methods=['GET', 'POST'])
def excluir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Você só pode excluir a si mesmo estando logado'})

    usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
    usuario.excluir()

    return redirect(url_for("inicio"))


@app.route('/controleSeguirUsuario', methods=['GET', 'POST'])
def seguir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    msg_erro, seguindo = current_user.controle_seguir_usuario(valores['idUsuarioSeguir'])
    
    return jsonify({'erro': msg_erro, 'seguindo': seguindo})


@app.route('/retornarUsuariosSeguindo', methods=['GET', 'POST'])
def retornar_usuarios_seguindo():
    valores = request.get_json()

    usuarios_seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=int(valores["idUsuario"])).all()

    return jsonify({'erro': '', 'usuarios': [u.usuario_seguindo.dicionario() for u in usuarios_seguindo]})


@app.route('/retornarUsuariosSeguidores', methods=['GET', 'POST'])
def retornar_usuarios_seguidores():
    valores = request.get_json()

    usuarios_seguidores = UsuarioSeguir.query.filter_by(usuario_seguindo_id=int(valores["idUsuario"])).all()

    return jsonify({'erro': '', 'usuarios': [u.usuario_seguidor.dicionario() for u in usuarios_seguidores]})


@app.route('/gerarRecomendacaoLivro', methods=['GET', 'POST'])
def gerar_recomendacao_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    calcular_recomendacao_livro()

    return jsonify({})


def retornar_idlivro_cache(id_livro):
    livros_cache = cache.get(session_key('livro_cache'))
    if isinstance(id_livro, str) and livros_cache is not None and id_livro in livros_cache:
        livro = livros_cache[id_livro]
        if isinstance(livro, Livro) and inspect(livro).transient:
            livro.id = None
            gravar_livro(livro)
            db.session.flush()
            livros_cache[id_livro] = livro.id
            cache.set(session_key('livro_cache'), livros_cache)
            return livro.id
        elif isinstance(livro, Livro) and not inspect(livro).transient:
            livros_cache[id_livro] = livro.id
            cache.set(session_key('livro_cache'), livros_cache)
            return livro.id
        return livros_cache[id_livro]
    return id_livro


@app.route('/livro', methods=['GET', 'POST'])
def livro():
    id_livro = request.args.get('id', '0')

    print("id", id_livro)

    img_usuario = ""
    reacao_usuario = ""

    livros_cache = cache.get(session_key('livro_cache'))

    if isinstance(id_livro, str) and livros_cache is not None and id_livro in livros_cache:
        if not isinstance(livros_cache[id_livro], Livro):
            id_livro = livros_cache[id_livro]
            return redirect(url_for("livro", id=id_livro))
        else:
            if current_user.is_authenticated:
                img_usuario = current_user.img
            return render_template('livro.html', livro=livros_cache[id_livro].dicionario(), img_usuario=img_usuario, reacao_usuario=reacao_usuario)

    try:
        id_livro = int(id_livro)
    except:
        return redirect(url_for("pesquisa"))

    livro = db.session.query(Livro).filter_by(id=id_livro).first()
    if livro is None:
        return redirect(url_for("pesquisa"))

    if current_user.is_authenticated:
        alterar_livro_em_alta(current_user.id, livro.id, clicado=True)
        img_usuario = current_user.img
        reacao_usuario = db.session.query(Reacao).filter_by(usuario_id=current_user.id, origem=OrigemReacao.Livro, origem_id=livro.id).first()
        if reacao_usuario:
            reacao_usuario = reacao_usuario.reacao.nome.lower().replace(" ", "")
        else:
            reacao_usuario = ""
    else:
        alterar_livro_em_alta(0, livro.id, clicado=True)

    return render_template('livro.html', livro=livro.dicionario(), img_usuario=img_usuario, reacao_usuario=reacao_usuario)


@app.route('/gravarReacaoLivro', methods=['GET', 'POST'])
def gravar_reacao_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para reagir o livro.'})
    
    valores = request.get_json()

    reacao_tipo = db.session.query(ReacaoTipo).filter_by(nome=valores['reacao']).first()
    if not reacao_tipo and valores['reacao'].strip() != "":
        return jsonify({'erro': 'A reação não é permitida.'})

    id_livro = retornar_idlivro_cache(valores['idLivro'])

    livro = db.session.query(Livro).filter_by(id=int(id_livro)).first()
    if livro is None:
        return jsonify({'erro': 'O livro não existe ou foi alterado. Recarregue a página e tente novamente.'})
    
    reacao = db.session.query(Reacao).filter_by(usuario_id=current_user.id, origem=OrigemReacao.Livro, origem_id=livro.id).first()
    if reacao:
        if valores['reacao'].strip() == "":
            db.session.delete(reacao)
            alterar_livro_em_alta(current_user.id, livro.id, reagido=False)

        elif reacao.reacao.nome != reacao_tipo.nome:
            reacao.reacao = reacao_tipo

        db.session.commit()

    else:
        nova_reacao = Reacao(
            usuario_id = current_user.id,
            reacao = reacao_tipo,
            origem = OrigemReacao.Livro,
            origem_id = livro.id
        )
        alterar_livro_em_alta(current_user.id, livro.id, reagido=True)
        db.session.add(nova_reacao)
        db.session.commit()
    
    return jsonify({'erro': ''})


@app.route('/retornarListasLivro', methods=['GET', 'POST'])
def retornar_listas_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    valores = request.get_json()
    id_usuario = int(valores.get('idUsuario', 0))
    id_usuario_tela = int(valores.get('idUsuario', 0))
    id_usuario_atual = 0
    if current_user.is_authenticated:
        id_usuario_atual = current_user.id

    if id_usuario == 0 and current_user.is_authenticated:
        id_usuario = current_user.id

    buscar_apenas_livros = False
    livros = []
    qtd_livros = db.session.query(Livro).filter_by(autor_id=id_usuario).count()

    if id_usuario == current_user.id:
        listas = db.session.query(ListaLivro).filter_by(usuario_id=id_usuario).all()
    elif db.session.query(UsuarioSeguir).filter_by(usuario_seguidor_id=current_user.id, usuario_seguindo_id=id_usuario_tela).first():
        listas = db.session.query(ListaLivro).filter(ListaLivro.usuario_id==id_usuario, or_(ListaLivro.visibilidade==VisibilidadeLivro.Seguindo, ListaLivro.visibilidade==VisibilidadeLivro.Publica)).all()
    else:
        listas = db.session.query(ListaLivro).filter_by(usuario_id=id_usuario, visibilidade=VisibilidadeLivro.Publica).all()

    if qtd_livros > 0 and len(listas) == 0 and id_usuario_tela != current_user.id:
        buscar_apenas_livros = True
        livros = [l.dicionario() for l in db.session.query(Livro).filter_by(autor_id=id_usuario).all()]
    elif qtd_livros > 0:
        pass
        #listas.insert(0, {
        #    'id': 'livrosproprios',
        #    'nome': "Meus Livros",
        ##    'descricao': "Livros que eu escrevi",
        #    'visibilidade': VisibilidadeLivro.Publica,
        #    'usuario_id': id_usuario
        #})
    
    return jsonify({
        'erro': '' if current_user.is_authenticated else 'Deve estar logado para acessar esta funcionalidade.',
        'listas': [{**lista.dicionario(), 'usuario_id': id_usuario_atual} for lista in listas],
        'buscar_apenas_livros': buscar_apenas_livros,
        'livros': livros
    })


@app.route('/retornarListaLivro', methods=['GET', 'POST'])
def retornar_lista_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    valores = request.get_json()
    #usuario_id = int(valores.get('idUsuario', 0))

    lista = db.session.query(ListaLivro).filter_by(id=valores['idLista'], usuario_id=current_user.id).first()
    if lista:
        lista = lista.dicionario()
        lista['usuario_id'] = current_user.id
        return jsonify(lista)
    
    return jsonify({})
    

@app.route('/controleListaLivro', methods=['GET', 'POST'])
def controle_lista_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()
    valores['id'] = int(valores.get('id', 0))

    alterada = False

    nova_lista = ListaLivro(
        usuario_id=current_user.id,
        nome=valores['nome'].strip(),
        descricao=valores.get('descricao', '').strip(),
        visibilidade = VisibilidadeLivro(int(valores.get('visibilidade', 0)))
    )

    if (msg_erro := nova_lista.validar_campos()) != "":
        return jsonify({'erro': msg_erro})

    if valores['id'] == 0:
        lista = db.session.query(ListaLivro).filter_by(nome=nova_lista.nome, usuario_id=current_user.id).first()
        if lista:
            return jsonify({'erro': f"Já existe uma lista com o nome '{nova_lista.nome}'."})
        
        else:
            lista = nova_lista
            db.session.add(lista)

    else:
        lista = db.session.query(ListaLivro).filter_by(id=valores['id'], usuario_id=current_user.id).first()
        if not lista:
            return jsonify({'erro': 'Lista não encontrada ou excluída'})
        
        lista.nome = nova_lista.nome
        lista.descricao = nova_lista.descricao
        lista.visibilidade = nova_lista.visibilidade
        alterada = True
        
    db.session.commit()

    return jsonify({'erro': '', 'lista': lista.dicionario(), 'alterada': alterada})


@app.route('/apagarListaLivro', methods=['GET', 'POST'])
def apagar_lista_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=valores.get("idLista", 0), usuario_id=current_user.id).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada ou já excluída'})
    
    if (msg_erro := lista.apagar_lista(current_user)) != "":
        return jsonify({'erro': msg_erro})

    return jsonify({'erro': ''})


@app.route('/retornarLivrosLista', methods=['GET', 'POST'])
def retornar_livros_lista():
    valores = request.get_json()
    print(valores)

    livros = db.session.query(ListaLivroLivro).filter_by(id_listalivro=valores.get("idLista", 0), usuario_id=valores.get("idUsuario", 0)).all()
    livros = [{
        **itemLivro.livro.dicionario(), 
        'idRelacao': itemLivro.id, 
        'idLista': itemLivro.id_listalivro, 
        'usuario_id': '0' if not current_user.is_authenticated else current_user.id
    } for itemLivro in livros]

    return jsonify({'erro': '', 'livros': livros})


@app.route('/retornarLivrosAutor', methods=['GET', 'POST'])
def retornar_livros_autor():    
    valores = request.get_json()

    livros_autor = db.session.query(Livro).filter_by(id=int(valores['idAutor'])).first()

    return jsonify([l.dicionario() for l in livros_autor])


@app.route('/vincularLivroLista', methods=['GET', 'POST'])
@conexao_commit
def vincular_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idLista']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    id_livro = retornar_idlivro_cache(valores['idLivro'])

    if (msg_erro := lista.vincular_livro(valores['idLista'], id_livro, current_user)) != "":
        print("erro aqui", msg_erro)
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/desvincularLivroLista', methods=['GET', 'POST'])
@conexao_commit
def desvincular_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idLista']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    if (msg_erro := lista.desvincular_livro(valores['idLivro'], current_user)) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/moverLivroLista', methods=['GET', 'POST'])
@conexao_commit
def mover_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idListaAtual']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    if (msg_erro := lista.mover_livro(valores['idLivro'], valores['idListaMover'], current_user)) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/controleSeguirLista', methods=['GET', 'POST'])
def seguir_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para seguir a lista.'})
    
    valores = request.get_json()

    lista_livro = db.session.query(ListaLivro).filter_by(id=valores["idLista"], usuario_id=valores["idUsuarioSeguir"]).first()
    if not lista_livro:
        jsonify({'erro': "A lista não existe ou foi alterada. Recarregue a página e tente novamente"})

    msg_erro, seguindo = lista_livro.controle_seguir_lista(current_user)
    
    return jsonify({'erro': msg_erro, 'seguindo': seguindo, 'idLista': lista_livro.id})


@app.route('/procurarComentarios', methods=['GET', 'POST'])
def retornar_comentarios():
    return retorno_comentarios()


@app.route('/procurarRespostas', methods=['GET', 'POST'])
def retornar_respostas():
    return retorno_comentarios(True)


def retorno_comentarios(resposta=False):
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para ver os comentários.'})
    
    filtros = request.get_json()
    filtros['limit'] = filtros.get('limit', '5')
    filtros['skip'] = filtros.get('skip', '0')

    if filtros.get('primeiroretorno', True):
        filtros['qtdItens'] = db.session.query(Comentario).filter_by().count()

    print('ffc', filtros)

    nivel_comentario = 1
    filtros_query = [
        Comentario.origem_id == filtros.get("itemOrigemId", "0"),
        Comentario.origem == OrigemComentario(OrigemComentario[filtros['telaOrigem'].capitalize()].value)
    ]

    if resposta:
        nivel_comentario = 2
        filtros_query.append(Comentario.comentario_pai_id == filtros.get('idComentarioPai', '0'))
    filtros_query.append(Comentario.nivel_comentario == nivel_comentario)

    comentarios = db.session.query(Comentario).filter(*filtros_query).order_by().limit(filtros['limit']).offset(filtros['skip']).all()

    return jsonify({'erro': '', 'dados': [c.dicionario() for c in comentarios]})


@app.route('/gravarComentario', methods=['GET', 'POST'])
def gravar_comentario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para comentar.'})
    
    valores = request.get_json()
    print('vv', valores)

    comentario = Comentario(
        usuario_id = current_user.id,
        usuario = current_user,
        conteudo = valores['conteudo'],
        origem = OrigemComentario(OrigemComentario[valores['telaOrigem'].capitalize()].value),
        origem_id = valores['itemOrigemId'],
        comentario_pai_id = valores['comentarioPaiId'],
        spoiler = valores['spoiler'],
        nivel_comentario = 1
    )

    print('origem', comentario.__dict__)

    if (msg_erro := comentario.validar_campos()) != "":
        return jsonify({'erro': msg_erro})

    if comentario.origem == OrigemComentario.Livro:
        comentario.origem_id = retornar_idlivro_cache(comentario.origem_id)

        if isinstance(comentario.origem_id, str) and 'cache' in comentario.origem_id:
            return jsonify({'erro': 'Erro de duplicidade de livro ao gravar comentário. Recarregue a tela ou tente executar novamente a consulta.'})

        livro_banco = db.session.query(Livro).filter_by(id=comentario.origem_id).first()
        if not livro_banco:
            return jsonify({'erro': 'O livro não existe ou foi alterado em banco de dados. Recarregue a tela ou tente executar novamente a consulta.'})

    notificar = False

    if comentario.comentario_pai_id != 0:
        # Foi definido que sera permitido apenas um nivel de gravacao re respostas por isso recupera com nivel_comentario=1
        comentario_pai = db.session.query(Comentario).filter_by(id=comentario.comentario_pai_id, origem=comentario.origem, nivel_comentario=1).first()
        if not comentario_pai:
            return jsonify({'erro': 'O comentário para ser respondido foi alterado ou não existe mais.'})
        
        if current_user.id != comentario_pai.usuario_id:
            notificar = True

        comentario.nivel_comentario = comentario_pai.nivel_comentario + 1

    if comentario.origem == OrigemComentario.Livro:
        alterar_livro_em_alta(current_user.id, comentario.origem_id, comentado=True)

    db.session.add(comentario)
    if notificar:
        db.session.flush()

        tipo = TipoNotificacao.ComentarioLivro
        link = f"livro?id={comentario_pai.origem_id}&comentario={comentario.id}"
        if comentario.origem == OrigemComentario.Publicacao:
            tipo = TipoNotificacao.ComentarioPublicacao
            link = f"publicacao?id={comentario_pai.origem_id}&comentario={comentario.id}"

        notificacao = Notificacao(
            usuario_id = comentario_pai.usuario_id,
            usuario_interagiu_id = current_user.id,
            titulo = "Resposta em comentário",
            conteudo = f"{current_user.nome} respondeu ao seu comentário.",
            img = current_user.img,
            tipo = tipo,
            link = link,
            obj_id = comentario.id
        )
        db.session.add(notificacao)
    db.session.commit()

    return jsonify({'comentario': comentario.dicionario()})


@app.route('/excluirComentario', methods=['GET', 'POST'])
def remover_comentario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para interagir com comentários.'})
    
    valores = request.get_json()

    print('orr', OrigemComentario[valores['origem'].capitalize()].value, valores['origem'], valores['idComentario'])
    comentario = db.session.query(Comentario).filter_by(id=valores['idComentario'], usuario_id=current_user.id, origem=OrigemComentario(OrigemComentario[valores['origem'].capitalize()].value)).first()
    if not comentario:
        return jsonify({'erro': 'O comentário não existe ou já foi excluído.'})

    for comnetario_child in db.session.query(Comentario).filter_by(comentario_pai_id=comentario.id, nivel_comentario=2, origem=OrigemComentario(OrigemComentario[valores['origem'].capitalize()].value)).all():
        db.session.delete(comnetario_child)

    if comentario.origem == OrigemComentario.Livro:
        alterar_livro_em_alta(current_user.id, comentario.origem_id, comentado=True)

    db.session.delete(comentario)
    db.session.commit()

    return jsonify({})


@app.route('/reagirComentario', methods=['GET', 'POST'])
def reagir_comentario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para interagir com comentários.'})
    
    valores = request.get_json()
    id_comentario = valores['idComentario']

    print('id_comentario', id_comentario)

    comentario = db.session.query(Comentario).filter_by(id=id_comentario).first()
    if not comentario:
        return jsonify({'erro': 'O comentário não existe mais.'})

    reacao_banco = db.session.query(Reacao).filter_by(usuario_id=current_user.id, origem_id=id_comentario, origem=OrigemReacao.Comentario).first()
    if reacao_banco:
        db.session.delete(reacao_banco)
    else:
        reacao = Reacao(
            usuario_id = current_user.id,
            origem_id = id_comentario,
            origem = OrigemReacao.Comentario,
            reacao = db.session.query(ReacaoTipo).filter_by(nome="Coração").first()
        )

        db.session.add(reacao)

        if comentario.usuario_id != current_user.id:

            tipo = TipoNotificacao.ReacaoComentarioLivro
            link = f"livro?id={comentario.origem_id}&comentario={comentario.id}"
            if comentario.origem == OrigemComentario.Publicacao:
                tipo = TipoNotificacao.ReacaoComentarioPublicacao
                link = f"publicacao?id={comentario.origem_id}&comentario={comentario.id}"

            notificacao_banco = Notificacao.query.filter_by(usuario_id=comentario.usuario_id, tipo=tipo, link=link).first()

            if notificacao_banco is None:
                notificacao = Notificacao(
                    usuario_id = comentario.usuario_id,
                    usuario_interagiu_id = current_user.id,
                    titulo = "Reação em comentário",
                    conteudo = f"{current_user.nome} reagiu ao seu comentário.",
                    img = current_user.img,
                    tipo = tipo,
                    link = link,
                    obj_id = comentario.id
                )
                db.session.add(notificacao)

    db.session.commit()

    return jsonify({})


@app.route('/procurarNotificacoes', methods=['GET', 'POST'])
def retornar_notificacoes():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    notificacoes = db.session.query(Notificacao).filter_by(usuario_id=current_user.id, lido=False).order_by(Notificacao.data_gravacao.desc(), Notificacao.lido).all()

    print('nt', [n.dicionario() for n in notificacoes])

    return jsonify({'erro': '', 'notificacoes': [n.dicionario() for n in notificacoes]})


@app.route('/removerNotificacao', methods=['GET', 'POST'])
def removerNotificacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    valores = request.get_json()

    notificacao = db.session.query(Notificacao).filter_by(usuario_id=current_user.id, id=valores.get("idNotificacao")).first()
    if not notificacao:
        return jsonify({'erro': 'A notificação não existe ou já foi excluída.'})
    
    notificacao.lido = True
    db.session.commit()

    qtd_notificacoes = db.session.query(Notificacao).filter_by(usuario_id=current_user.id, lido=False).count()

    return jsonify({'erro': '', 'qtdNotificacoes': qtd_notificacoes})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        #gravar_livros_aux2()
        #gravar_imagem_autor(
        #    ''
        #    ,"Machado de Assis")


app.run(debug=True, host="0.0.0.0", port=144)

#finalizar_crawler_drivers()
print("fim")
