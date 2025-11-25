from datetime import timedelta
import hashlib
import json
import os

from flask import Flask, g, render_template, request, redirect, session, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from sqlalchemy import inspect, func
from unidecode import unidecode
from werkzeug.utils import secure_filename

from publicacao import publicacao_bp

from python.banco import db
from python.cache import init_cache, cache, session_key
from python.crawler import atualizar_precos
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


# .\venv\Scripts\python.exe -m pip install --upgrade scikit-learn


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
    return dict(generos=g.get("generos", None), idLivroMaisVisto=retornar_id_livro_mais_visto())


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

    if request.method == "GET":
        return render_template("login.html", nome="", senha="", **request.args)
    elif request.method == "POST":
        nome = request.form['campoNome']
        senha = request.form['campoSenha']

        usuario = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not usuario:
            return render_template("login.html", erro="Nome ou senha incorretos", nome=nome, senha=senha, **request.args)

        usuario.ativar()
        login_user(usuario)
        dic_request = request.args.to_dict()
        if "pagina" in dic_request:
            del dic_request["pagina"]

        if pagina_solicitada == "criarpublicacao":
            pagina_solicitada = "publicacao.criar_publicacao"

        return redirect(url_for(pagina_solicitada, **dic_request))


@app.route("/usuarioEstaLogado", methods=["GET", "POST"])
def usuario_esta_logado():
    return jsonify(current_user.is_authenticated)


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

    dic_generos = {v['nomeCampo']: False for v in retornar_generos_literario()}

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

        retorno = processar_filtros(filtros)
        retorno = [r.dicionario() for r in retorno]
        #print(retorno)
        return jsonify({'erro': '', 'dados': retorno})


@app.route('/pesquisaLivros', methods=['POST', 'GET'])
def pesquisa_livros():
    filtros = request.get_json()
    filtros['checkLivros'] = True
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


@app.route('/sugestaoPesquisaLivrosSugeridos', methods=['GET', 'POST'])
def sugestao_pesquisa_livros_sugeridos():
    id_usuario = current_user.id if current_user.is_authenticated else 0
    livros = db.session.query(LivroRecomendado).filter_by(usuario_id=id_usuario).order_by(LivroRecomendado.data_criado.desc()).limit(12).all()
    return jsonify({ 'livros': [livro.livro.dicionario() for livro in livros] })


def retornar_id_livro_mais_visto():
    #livro = db.session.query().filter_by(clicado=1).
    registro = (
        db.session.query(LivrosEmAlta.livro_id, func.count().label("qtd"))
        .filter(LivrosEmAlta.clicado == 1)
        .group_by(LivrosEmAlta.livro_id)
        .order_by(func.count().desc(), LivrosEmAlta.data_alterado.desc())
        .first()
    )
    if not registro:
        livro_id = db.session.query(Livro).order_by(Livro.data_alterado.desc()).first().id
    else:
        livro_id = registro.livro_id

    return livro_id


@app.route('/usuario', methods=['GET', 'POST'])
def usuario():
    id_usuario = request.args.get('id', '0')
    interacao = request.args.get('interacao', '')
    pagina = None if request.args.get('ignore', None) is not None else "Usuário"

    if not current_user.is_authenticated:
        return redirect(url_for("login", pagina=pagina, id=id_usuario))

    usuario_tela_logado = False

    if id_usuario == '0' or (current_user.is_authenticated and int(id_usuario) == current_user.id):

        usuario = current_user
        usuario_tela_logado = True

    else:
        usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
        if not usuario or not usuario.ativo:
            #flash("Usuário não encontrado", "error")
            return redirect(url_for("pesquisa", tipoFiltro='autor'))
        alterar_pessoa_em_alta(current_user.id, usuario.id, clicado=True)

    usuario.usuario_tela_logado = usuario_tela_logado

    return render_template('usuario.html', usuario=usuario.dicionario(usuario_tela_logado=usuario_tela_logado), interacao=interacao, imagem_capa=usuario.retornar_img_capa())


@app.route('/alterarImagemCapaUsuario', methods=['GET', 'POST'])
def alterar_imagem_capa_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Você deve estar logado para alterar a imagem de capa'})

    current_user.atualizar_caminho_imagem(request.get_json()["imagem"], transformar="perfil_capa")
    db.session.commit()

    return jsonify({'erro': '', 'imagem': current_user.retornar_img_capa()})


@app.route('/retornarImagemCapaUsuario', methods=['GET', 'POST'])
def retornar_imagem_capa_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Você deve estar logado'})
    
    valores = request.get_json()

    usuario = db.session.query(Usuario).filter_by(id=valores.get('idUsuario', '0')).first()
    if not usuario:
        return jsonify({'erro': '', 'imagem': usuario.retornar_img_capa()})
    
    return jsonify({'erro': '', 'imagem': 'static\\imagens\\sistema\\perfil_capa.png'})


@app.route('/desativarConta', methods=['GET', 'POST'])
def desativar_conta():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Você só pode desativar a conta estando logado'})
    
    current_user.desativar()

    logout()

    return jsonify({'erro': ''})


@app.route('/excluirUsuario', methods=['GET', 'POST'])
@conexao_commit
def excluir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Você só pode excluir a si mesmo estando logado'})

    usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
    usuario.excluir()

    return jsonify({'erro': ''})


@app.route('/controleSeguirUsuario', methods=['GET', 'POST'])
def seguir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    msg_erro, seguindo = current_user.controle_seguir_usuario(valores['idUsuarioSeguir'])
    
    return jsonify({'erro': msg_erro, 'seguindo': seguindo})


@app.route('/retornarUsuariosSeguir', methods=['GET', 'POST'])
def retornar_usuarios_seguir():
    filtros = request.get_json()

    usuarios = processar_filtros(filtros)
    return jsonify({'erro': '', 'dados': [u.dicionario() for u in usuarios]})


@app.route('/retornarUsuariosSeguindo', methods=['GET', 'POST'])
def retornar_usuarios_seguindo():
    filtros = request.get_json()

    usuarios_seguindo = UsuarioSeguir.query.filter_by(usuario_seguidor_id=int(filtros["idUsuario"])).all()

    return jsonify({'erro': '', 'usuarios': [u.usuario_seguindo.dicionario() for u in usuarios_seguindo]})


@app.route('/retornarUsuariosSeguidores', methods=['GET', 'POST'])
def retornar_usuarios_seguidores():
    filtros = request.get_json()

    usuarios_seguidores = UsuarioSeguir.query.filter_by(usuario_seguindo_id=int(filtros["idUsuario"])).all()

    return jsonify({'erro': '', 'usuarios': [u.usuario_seguidor.dicionario() for u in usuarios_seguidores]})


@app.route('/alterarPlanoUsuario', methods=['GET', 'POST'])
def alterar_plano_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para ter um plano.'})
    
    msg_erro = current_user.atualizar_plano(request.get_json()['novoPlano'])

    return jsonify({'erro': msg_erro, 'plano': current_user.plano.value})


@app.route('/gerarRecomendacaoLivro', methods=['GET', 'POST'])
def gerar_recomendacao_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para receber recomendacao de livros.'})
    
    tem_notificacao = calcular_recomendacao_livro(current_user.id)

    return jsonify({'tem_notificacao': tem_notificacao})


@app.route('/retornarCoresUsuario', methods=['GET', 'POST'])
def retornar_cores_usuario():
    if not current_user.is_authenticated or (current_user.plano != PlanoPerfil.Padrao and current_user.plano != PlanoPerfil.Premium):
        return jsonify({})
    
    return jsonify({
        "corPrimaria": current_user.cor_primaria,
        "corSecundaria": current_user.cor_secundaria,
        "corTercearia": current_user.cor_tercearia,
        "corDestaque": current_user.cor_destaque,
        "corFundoContraste": current_user.cor_fundo_contraste,
        "corFundo2Contraste": current_user.cor_fundo2_contraste,
    })
    

@app.route('/salvarCorUsuario', methods=['GET', 'POST'])
def salvar_cor_usuario():
    if not current_user.is_authenticated or (current_user.plano != PlanoPerfil.Padrao and current_user.plano != PlanoPerfil.Premium):
        return jsonify()
    
    usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
    usuario.atualizar_cores(request.get_json())

    return jsonify()


@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if not current_user.is_authenticated:
        return redirect(url_for("login", pagina="configuracoes"))
    
    return render_template("configuracoes.html")


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

    if img_usuario is None or str(img_usuario).strip() == "":
        img_usuario = "static\\imagens\\usuarios\\anonimo.png"

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
    filtros = request.get_json()
    filtros['limit'] = filtros.get('limit', '20')
    filtros['skip'] = filtros.get('skip', '0')
    filtros['campoPesquisa'] = filtros.get('campoPesquisa', '').lower()

    condicao = [ListaLivroLivro.id_listalivro == filtros.get("idLista", 0), ListaLivroLivro.usuario_id == filtros.get("idUsuario", 0)]
    if filtros['campoPesquisa'] != "":
        condicao.append(Livro.titulo_aux.ilike(f"%{filtros['campoPesquisa']}%"))
        livros = db.session.query(ListaLivroLivro).join(Livro, Livro.id == ListaLivroLivro.id_livro).filter(*condicao).limit(filtros['limit']).offset(filtros['skip']).all()
    else:
        livros = ListaLivroLivro.query.filter(*condicao).limit(filtros['limit']).offset(filtros['skip']).all()

    livros = [{
        **itemLivro.livro.dicionario(),
        'idRelacao': itemLivro.id,
        'idLista': itemLivro.id_listalivro, 
        'usuario_id': '0' if not current_user.is_authenticated else current_user.id
    } for itemLivro in livros]

    return jsonify({'erro': '', 'dados': livros})


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
@conexao_commit
def seguir_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para seguir a lista.'})
    
    valores = request.get_json()

    lista_livro = db.session.query(ListaLivro).filter_by(id=valores["idLista"], usuario_id=valores["idUsuarioSeguir"]).first()
    if not lista_livro:
        jsonify({'erro': "A lista não existe ou foi alterada. Recarregue a página e tente novamente"})

    msg_erro, seguindo = lista_livro.controle_seguir_lista(current_user)
    
    return jsonify({'erro': msg_erro, 'seguindo': seguindo, 'idLista': lista_livro.id})


@app.route('/retornarPrecosLivro', methods=['GET', 'POST'])
def retornar_precos_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para retornar ver os preços.'})
    
    if current_user.plano != PlanoPerfil.Premium:
        return jsonify({'erro': 'Usuário não tem permissão para ver os preços.'})

    if 'idLivro' not in request.get_json():
        return jsonify({'erro': '', 'dados': {}})
    
    try:
        int(request.get_json()['idLivro'])
    except:
        return jsonify({'erro': '', 'dados': {}})

    registros = (
        LivroPreco.query
        .filter_by(livro_id=int(request.get_json()['idLivro']))
        .join(LivroLink)
        .order_by(LivroPreco.data_consulta)
        .limit(12)
        .all()
    )

    dados_por_link = {}
    links_carregados = {}
    for r in registros:
        if r.link_id not in links_carregados:
            livro_link = db.session.query(LivroLink).filter_by(id=r.link_id).first()
            if livro_link:
                links_carregados[r.link_id] = livro_link.hospedeiro
            else:
                links_carregados[r.link_id] = r.link_id
            dados_por_link[links_carregados[r.link_id]] = []

        dados_por_link[links_carregados[r.link_id]].append({
            "data": r.data_consulta.strftime("%d-%m-%Y"),
            "preco": r.preco,
            "preco_usado": r.preco_usado,
        })

    data_add_nova = ""
    data_add_antiga = ""
    for l, v in dados_por_link.items():
        if len(v) > 0:
            data_mais = datetime.strptime(v[-1]['data'], "%d-%m-%Y")
            data_menos = datetime.strptime(v[0]['data'], "%d-%m-%Y")

            if data_add_nova == "" or data_mais > data_add_nova:
                data_add_nova = data_mais

            if data_add_antiga == "" or data_add_antiga > data_menos:
                data_add_antiga = data_menos

    for l, v in dados_por_link.items():
        if len(v) > 0:
            data_mais = datetime.strptime(v[-1]['data'], "%d-%m-%Y")
            data_menos = datetime.strptime(v[0]['data'], "%d-%m-%Y")

            if data_add_nova > data_mais:
                aux = v[-1].copy()
                aux['data'] = data_add_nova.strftime("%d-%m-%Y")
                dados_por_link[l].append(aux)

            if data_add_antiga < data_menos:
                aux = v[0].copy()
                aux['data'] = data_add_antiga.strftime("%d-%m-%Y")
                dados_por_link[l].insert(0, aux)

    return jsonify({'erro': '', 'dados': dados_por_link})


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
    comentario_pai = None

    if comentario.comentario_pai_id != 0:
        # Foi definido que sera permitido apenas um nivel de gravacao re respostas por isso recupera com nivel_comentario=1
        comentario_pai = db.session.query(Comentario).filter_by(id=comentario.comentario_pai_id, origem=comentario.origem, nivel_comentario=1).first()
        if not comentario_pai:
            return jsonify({'erro': 'O comentário para ser respondido foi alterado ou não existe mais.'})
        
        if current_user.id != comentario_pai.usuario_id:
            notificar = True

        comentario.nivel_comentario = comentario_pai.nivel_comentario + 1

    livro = None
    publicacao = None

    if comentario.origem == OrigemComentario.Livro:
        alterar_livro_em_alta(current_user.id, comentario.origem_id, comentado=True)
        livro = db.session.query(Livro).filter_by(id=comentario.origem_id).first()
    elif comentario.origem == OrigemComentario.Publicacao:
        publicacao = db.session.query(Publicacao).filter_by(id=comentario.origem_id).first()
        if publicacao:
            if current_user.id != publicacao.usuario_id:
                notificar = True

    print('livrooooooo', livro)
    print('publicacaooooooo', publicacao)
    print('publicacaooooooo', comentario_pai)

    db.session.add(comentario)
    if notificar:
        db.session.flush()

        tipo = TipoNotificacao.ComentarioLivro
        link = ""
        titulo = "Resposta em comentário"
        msg = ""
        usuario_id_outro = 0
        if comentario_pai:
            usuario_id_outro = comentario_pai.usuario_id
            link = f"livro?id={comentario_pai.origem_id}&comentario={comentario.id}"
            msg = f"{current_user.nome} respondeu ao seu comentário no livro."
            if comentario.origem == OrigemComentario.Publicacao:
                tipo = TipoNotificacao.ComentarioPublicacao
                link = f"publicacao?id={comentario_pai.origem_id}&comentario={comentario.id}"
                msg = f"{current_user.nome} respondeu ao seu comentário na publicação."

        elif publicacao:
            usuario_id_outro = publicacao.usuario_id
            tipo = TipoNotificacao.ComentarioPublicacao
            link = f"publicacao?id={publicacao.id}&comentario={comentario.id}"
            titulo = "Comentário em publicação"
            msg = f"{current_user.nome} respondeu a sua publicação."

        if msg != "" and usuario_id_outro != 0:
            notificacao = Notificacao(
                usuario_id = usuario_id_outro,
                usuario_interagiu_id = current_user.id,
                titulo = titulo,
                conteudo = msg,
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


@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    if not current_user.is_authenticated:
        return redirect(url_for("login", pagina="notificacoes"))
    
    if request.method == "GET":
        filtros = {}
        filtros['checkNotificacoes'] = True

        filtros['qtdItens'] = processar_filtros(filtros, retornar_quantidade=True)

        return render_template("notificacoes.html", filtros=filtros)

    elif request.method == "POST":

        filtros = request.get_json()
        filtros['checkNotificacoes'] = True

        print('Segundo retorno')
        retorno = processar_filtros(filtros)
        retorno = [r.dicionario() for r in retorno]
        #print(retorno)
        return jsonify({'erro': '', 'dados': retorno})


@app.route('/procurarNotificacoes', methods=['GET', 'POST'])
def retornar_notificacoes():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    notificacoes = db.session.query(Notificacao).filter_by(usuario_id=current_user.id, lido=False).order_by(Notificacao.data_gravacao.desc(), Notificacao.lido).limit(5).all()

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


@app.route('/recuperarSenha', methods=['GET', 'POST'])
def recuperar_senha():
    return render_template("recuperarSenha.html")


@app.route('/recuperarSenhaConfirmar', methods=['GET', 'POST'])
def recuperar_senha_confirmar():
    
    valores = request.get_json()

    usuario = db.session.query(Usuario).filter_by(email=valores['email'].strip()).first()
    if not usuario:
        return jsonify({'erro': 'E-mail não encontrado no sistema.'})

    usuario.recuperar_senha()

    return jsonify({'erro': ''})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        #gravar_livros_aux2()
        #gravar_imagem_autor(
        #    '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPoAAADNCAIAAAAe8fp/AAAQAElEQVR4AeydYXoaPc+F/XzLGfpP71bIEibLCF0GLAG2Uv8r3U6++xzZAyQkIQlJaEMvo7FlWZalY4/HQ+j/3V//XT3wbTzwf+X67+qBb+OBK9y/TaivAy3lCvcrCr6RB65w/0bBvg71CvcPwMBV5aV64Ar3S43M1a4P8MAV7h/g1KvKS/XAFe6XGpmrXR/ggSvcP8CpV5WX6oEr3C81Mle7Dj1wltIV7mdx41XJ3+GBK9z/jjhdrTyLB65wP4sbr0r+Dg9c4f53xOlq5Vk8cIX7Wdx4VfJ3eOAK98M4XUv/tAeucP+nw3sd3KEHrnA/9MeJpT+l/Kl1U8um1p+r+tP0ZlVJP5Lern7cVtJ/t6v/buuO/u/lfLZCDw1vUGKFaFZH9LVq/dL7n1qw5ESbr2LX77s/iYE/ZUKVQAzaQJ5RC3xXs/+tZqtys1rdrMqi1sWt6EZArNuV5sC2xLZUUilRat3ReDpfo5Raqhoiv10hWTcoYVJJc1FHVTSNoffZajVjLv3PU2s3K2SAJsOTg/u2FdfVnXW6JD4arH9oPQZGRvMttG6MYJAHCgGkaCQ0jZsqhnJiOg8HOcG3cAXwuqhWFTuOBKpqzS45E0QlLr4/Xd5MumnC5IK5IW5ohuQ0w9RFZRJqLMxJ7g8kJiozhJuD5kA2p/V3TN8P7t6EaAcCAjqyVzd7sGZhFsJAA8gQ+EJAFDRhGc1UU0UpEQytlAGfKbVwVMsHeS3YylHJBT2pkyJT5gFHRT7uEaynWskL1TCoE02+Okrl1pVi6KSEEDIygwK3CM3nRWXqclPi7qRdFsP/rAkgqy/j8w3gnvgmujdatutMN/3CxoClbqsgAFNAqRwg0WUCiuBSAJWYAhOSoAfa5SlRt5PvwnDQJQonsdubpB6USrnbA9ADJeiHb9qqqO5KqFGJigS61YrZi+SplAwfJyYY3e0oJhV2WRv2YN6PsSPiDsADAy7CJyQ3+yfJvwh3b7t1Nze+Wc9Y1bwRzwgCCDKiCRG2E8ZWAyjAolqY8IdiirWS6oQnM6POSszGmJcyjyAtlrEeY70c12PZLkelX3E/KnO/jPvl6JSZpHCc+eWMJMv217h18zWqxrJYxiKa/nmUmSzwR2ZMVoVuQQyB6aShmZ8oh5P8fSr0FxhSpLweM9gI8Txgp7XlH+jzNCyZf+Tzr8B9WsLZn8xuC7tVQrVRkOLgSbECbnEdaUPEwXYxww9Y3CSMJkqIC2QxH4U5kLcGlKRfsV2Ov5fxewTfRvkYdyEZQAn0hyhDUUI5GdS8nNQkEB4iaI4S0l3E3RiGvjr6rTmjGbJN5rIsNNM0DdpMCCxnmNBC1+60tl1+Dgeac2B/PohpWTfnvseTN+t9rv1kcudjib+X/M1w76u4NqO5RSFCxEnRINbET7kMeYbfNPlJEWiShjjoMH9mAAGj9TK2IHsZwDoBB/JAM1gUKGn+dQkbmAwkTMI2pgFGMgdIFDFyXjQHZCBTOvHNYClD4Rxg3Z5JzkSN+5wnrB259Wfbw1LykwNQOwplf1X6C+G+qdqoaBX/n3cpK0UvowJche5KKKIQYK5EQzR2a3xGkUatSpFmXZyPrKBlvRzvO7iBEaABVQOSf0ka+m0BxDMWTYDluOYOMLLj0tZLuxwcksOHkgff4Rx5rowU1+FKuVHupN6tXM3bhlIWHICutMpo1YdNk78j/TVw16scbyt1yrap7DVDgCYqGZuoRrziAq85P6MIrWDaPMKZ4akBlBcjm+wdvude1C3375ChaH91F2yEtPXa8nSx1NjnGiJuwSN2GkUcBbS18JujGj5dJmvNQNbermz3gT5LPk+6f8OSf9lwzx05CzkO5VXORm7G3wQDWtPjBEhsQDzhHryDb7gwRXvACHyJxbKw+b7/xVrOnhgoIPGN0lDAusbO2n/Pwj+WRcQsugfw2EM3xu7GKMcWiKSzCZQmpXDUs7itbPTBPa/eLvUB9yLhrk35qv7QHVPblS0Oxqd4Vm4G65PHzU0+VMtSnwNailKMWBJgQ9wL292/uISnY95AuaGxZ/u9LAl9dnRSosVCDsXxWk3IcsGl8KHkm6sla5kMhCi431ROw3S283N1ad9xuCy4c1xY2bHoaIXtCt7Dv7gTml5ueXsZ0pxONIzy3bJEHU9pwSnKdmxPmWxdxL1+jnsAH3Kj06ov3OvoMzf6uWSwxCCQN0lc3ZkEhdAQFCpRS7zaTEDe6z24v70o3F8G3DeVp08efbSWb3BfxXN2IQ7Fg1Bx5EQq5WwVo+zjG3Ea6Swi1jFu/bjJujXAJxLX9BoPeMnXRn89xmLn5L6rSZfa2w6H44J+8WMXFC1GVPGUVRbGPc+1nPAg+HXpi+HelnN2e80RkxMrue5f8pMr5cS9ZQbPIci7Ho4L+okhB+QD/Gt6twfmweONHuUb7ll3WH3AuCJCSOT6ZBQuGZpGtSip/9ZE9RsWtdvKY9jXbXK+CO7sznmB999t4RB3I6/IHfqkd3AZzoS/ox36WmwkSGWRcGG7mTuWu7FcUS63fMAn1/v7ZVlHzAlBxkVoj7ack08mtcwH8nCwpNEuptq6qHV2y66VxQ6Jz0yfDndNcZ5Bb+smz8sDHHvAOAg3VbtH+Y5pcZDpK7pktHLw9n4xxv0YLDzXHYs9+AkkWFzW3EVHQF90nuNwsbITltY9SxVlqJCtSImfASUneUez1E3R3pWTnHZjp/bD0+fBnamsDbo2cAJ6dwQjxBcHmO5Al79YFVxEJp1YtJwDcV6g8MZ+52X0XNNneWAIrTKEgFPdGZ1mpDKImYeCeKqEbyLIxSgPAumVCwYB9Qkmd3hAz7E94h+cPgPuAvoP9i0rVnSGEwVfgFN5B0fAAfqTF3DDJOAqMfRBiE05QCddj1nsmi8ncRft4Mugx566exlCSGFAFT1fEusUk98woHBzfMmxvUC/ou7j0gfDfVNZ0ZUYD3hlgJ7SRjkeoAz0tQx0N4npWoaceVFunW3fcgU6jrmwpOhwcu9lSNg9CDTxBuUVjHt1V8R7fM1TQQBQI0CyqHqW/bDtzUfBvfJClIdRHblovjJUYGtMg2+NOcfaOIof9Xmp3OyU06dyGDzyJLoe5Q5xrp8L9YBAT5gEeiA+hZg4Y3AGF0pwW5UDqto+Q7JKVE+xrPQfAPoPgLtPXcqMrQuDITFIxj+hHA7jF52wzmSAVZDSBXlP93mJ7S/2iOX6JCq3/B0fg5631yOv+QgoK5fC2SLLEHYrPQUjnmuCgSrkRMVnpecxj239WUF/Zrhrm84Z00Z/VmwQM1jGw4QWghPfKsPQmJgDyWeQTGsoA+YQPXjnH+tlDJa9kr/NAx30S8IPlsPhLootI4E3USrhKu69Fhgg3emm6PTmfOf0Z4O7gM4NiBmph5XdkKqKGhIjY9i9mCjfDXtaBmLhp5/rHh3f/NVpKAI9J8VzFrVEcHhAAAE8JADCa6LZiOgqDmBQ1hwAUxZ+KXuOZf48cM+/dC7+04oo0/Cwl7G1QXLB9KzVys6QdamWoLKUeRnZvfC2yGO9kn/CA8F2lORDegbkaCvugIQ8HIfeYDA8yIF4+FnLrEASIBVt6HkUfN93Ld8L97aoLzArgZu0Gc00ZfpieBQZrWFS0y4a1U6AR5z1sgyM85rO44HL0aJlnkP6OREXDCZI2ELQwRXQA6GDWipCsIEv0Ci/4QVlPhPS5C3pXXBnUdfWauvJVxgMZmE3dmAq+TQUjoql72r6aDUxYJZZf0tHu2v6dz0QeW4zAxgJlQaPxENbAwUIajs25A3mQEpCqWKZ929JqOrVn7fC/U9d/ViVhR5JsRA4p9FQmwDEmQPNUI8ENkwEp9HK9FiM8Xu8nr2U7/FvWubZt3RUgGwhwQ4AIcBm4qgIurSuq1pFGnLhfaWO51+/sXkT3Dc8OqxiuzMLlLMtkUlYC56VE7KnIYmhP4qZBuZaNjDXnbpd860Iy/y4GPuQBQnQEIIH6Gmg2uOwaIpvebH10San6LD7lV89eDXc68+6ulmlcaUhG0s05fQRwLHPJsFuY4CDxVkPt143MHjhW6e7EdDbA+AbbICkMD5MVAE/OexhdrUAj8q2xoOuxes2Nq+DuzbrC96SNlOEbTrHGFEM5UIV1pMH8RSxODlJjXsOGdnGDcggcE3f1ANsbMp2qT+t1KoptCSIO6gacnox8QOFj8cSPOSrDktubk/8K8FT4V71rvS2LuiP2Zad2UQ9gBrETDWZNlUlk6mATaIaFAI8nl/fHxGvawIMQ4nfyzrT+hg7h4AxOMJMruWuaSiCA+w6TZlixK/KCVv50+D+p5TdDwEkjrFJFmCzrWnFKvQ3IxLf0LRPksL6aPnTyAkDOE3RVepkDxBrAniy+PsFx9/LMssuw9qEqz0gAS3QP9Emg2SX0fpbt5U99otr/Mtw17q+uK2bNKjSjRO9Zj5pM1GYVnVjKtsPKLl59e2a2c+SnK/tD9oVgGelr5Xv8cCf2rzNS/Eft6vZLWdu9Yf2xPWzlhvW+JjlGBI50FxVQR1IowoK4gWzAg+GFlbJGHLIl9gW/ZLzsza/DPfCxmiDeuYQVL1ycZfqrB8SqT86zrsMmZSBm5yYlxOxjosrL8/83SC15U3thqcF67uSs3qAJzFczZpCiEF8bIv+jJrgKeOftJ/dCvfneHv/ouFC/BwgC9B5yhcCWaIOHKEgq+DsgAdCqMBkaGUCCPHsaigdTy/AXf8tBIOXPvqgJxlkTTJGH/pQmSwXzFIGI5xTnqZM3OCNKfUvJQKg06VNZcA0Nq0FxL/U8Fp/ugdAtlD+X/6PIwSKhLNRQKZtG4gaZdGtlvnyOYhvfxu1M8OLKagDe82w5Ng2iclCIKlyEwMtlQVanCOf5+COU2iMJyb40gN5q3FWOep10VTEpMwqgwAFUzZnZF9K6k6PwshhOoNIGoTnlKcQmv0z6YMG0u6c/i1fwqblUD2R5bK/xKjIh5h6xWGT8K5X91Z1AhnKuF5mj6aYRCvME4omDoiHW4wxKihCXRQbfHKPqj9uVXj0eRLuWmg1p6WKnhh5b0v3YJE7S1ojAWqRoQIPTmJUYErZjvA788mrIrGpbmIiQea0EE9WiOdyOYn97s1Kt76bxAE2X45xxy1RQP1HCDzVEREiRXSwW/gQWODREEbSLBJlYq0oqDk1H52GMm5HjKD7RBTQKkK2PnBcxAhEoDvzJj4yasuW5OeRPfBxuAO+0hZatZXiIvCRKQxf/QNNdaasuMqnB1XqMmU9xmnn66Edi93aHm2Vt3IPDGM096z7AgiIYQZiM7QI9/oP8V48Fvgqw/Egq11dcMUEHEsoyRBZaIsjdZwllHkyRcUp1IIz5P0fpB0DECrOnIaIhQwAabaB3rEhLTFD/TUBZakU3pITXKo32HWRK5FFOjkGd05CWLSENbQjiAYo+dQ10WaBKnZ+oXP4kinzUR6k6SlpHjEbm6HqmkESGMYhVfDLNO9neAAAEABJREFUK18Xn9Ln22U2NGXcolyCtYQJyeP1s8cCSH9NIpr6Gh9xITo4ForV2ALF7YVVabzXnyDxiEWGYuB46hEsu1afs4On27gbK3ggp4SRWJMwgMoeZoJqvASDzraiJ8pVAY9LFM48DiNyBO6aFl5rhTpa0ZfU0xO5hGDSVJoSWUse48TXhVenME5P3ApmCoZ6Uyvl8btUMbB8ZhL/Aj5/8IDMw0WMtqajcRr+vQDrHpoga0FJi5FdmnmwHpyYPViVVORVoIH+YIC67T/U/iHlcTHStVXjYE+7dLJv/q4CF/AVheimFhCqOgZLlWht9zRrevz/qnJ3rv7BI7WSDG3kmlQEk07o3xSCBKWmml4RgIXw+Fqs03Iocr3OXyOVcNmbuJG2ueqLiR6GMNjOZbBk8QXDh36xZUe7H8AEvqROBtqlhNXFeRz9OqoQr19NmiKLBuU5uqDZZ6ShlPW+zdP6oiHYAGpbPkfUmVxVZSYvXFfABlYpIo9Wd+3PkKYudYF1uSZKHzA1DFxBpoqAYwdUrNYBwceJJEm+8jP4L/f8jm3q0XZgkq83eifySqXnFvf9MQpuCZsl6j7ixAcVC38eiUVwFuz+ZK8+bY0sMZh9lMw1LseUkSKB/+Mzn0+CzbCQIDPAFBYAuug4xJo9JghEbLITWYowkfKWBobTAdx5+mbdciCBb8O3B6yW3U1SioybQ1IMimqKohhK7s1Jbxw0ThSgjW4xBgP6ADQhqfqyhIvcN4Y1V9hK53ULduVFEU4Lfi9BvO1UpGS6wKL/OfBJSwckd56XOEFQerLF+SvuRpBms+3ekiaRFxhAv3vM0ZAlg8HITEuwOIgBbKpJB3DvzyIpRG3TS399tAxXPXkOUIt2V8L2giE+6zqJ1u9IQryUpCWtCy6a3Lw5+8GbM0rv6OA9TXVGlL3jCpwAZfyhDcDwHr0f2FZ+HCKhsxfK+sztiCak2nbMCSAYH2jkY9VyqfdUthknT2Y0/wNlWgl1mUOEsmZFSiaNyg6eA5j9vTszgHWre6SpY3zVA7Y2SsJ31nULcCKdQAm8avthlrp9z0f7+DkzFZ1Q7FbvNqPE9uu2NH+0HQw5FMN2A2ek0faaZC80JSxsnJzJKJw/TqpvsMgAgIz1cbmP5rY/ABLo0hiZLt/TMZALF1ULNixAHUWzyRIiWQ9gdAy/t7pr0UKF5NwMhCELBW20E0Wj2upDTzDRSxPRdGXN/6IR3jmSEP/w5/Q1PAJQOfj7il0NJ+4avUanUeOQHHjoqFiuU80zH2YLx4I3+v+7V//d8rqbB6lPOu7Q92wJqKKG6X1de9pWnV0iLwB0oefuBl3mzFcWeG/DiHtCbsIhHcFsFnpEVGEtnOTnSDPvBX5a3eV0DS81JqWxNBJRLkmjrWoINC32mvJNYD5a+GyEI1gGXH2HSWA5b2CB+DZFz9bdy4p2c0z+wSEF94KktgiVJzXki9jZLa4uG0kxhkqGs0u97GR7JuYHfrQXb2hwL1F0CObsUbKpVW7PYZIHPc/u9Y8qOQtT21oU4TB8rSF4xQHhMElYKCZlwoHNsBQUfYRMOGoJd1P76r6hAUNKvmgXspJdS8Y8iVFF92iEA59eS8zReubkNX5MpbbKHRW6rrxHEHqy7hMokNWioK7lI67qNMpLWMfIyqKuyYmfaXZA5cebulqAeGWl8gM+oc2rrRaI04YsPtGZrG0CXmhalJ+Q/kB2P/mQcxLQmGWTchR0DQO6b6E4fACM54Zr9+Ge7YUiquSRRFVS9ZRVe2JoA+V0ScY9sVoM5NX+vB/W+Hwk8GjRnfbINhBffDII96NT5YlHfdC7urYx+v9Zuf+I/cQnsV54CSXHqyFXVEDdAo+5tFl1/Wafm9TBvRAuBQ3tvV+yj5Ie5IQBpDUzXf91z+JD6fuZtCd9mMOJhKUpK28K7FMEMB/h4CRGq/u0d6waoXQ5kPIKHGR7UsvQeTNViMkRCIhb1FMisguf+eo1nq6we9d7YVzF39f7BMSz7e73QOzIroFsLMbyzD9uCPpLdgzt7poV3sGN9yMjKnPGQmPrY6MI4rWmwvmIFHTDatVV1/LU2rSpVRMbcWR3gS56PoHzFUmmVmJvZMqTJT0nNE7joh7bMJsMZiMBlTCjTq7gXjYtGFZRaVGF+2QiBgOanUFTezKhmeCXJ92XIu+mXuMnbGESGj0eFk7Co5s1nI9Klc3Gzrk4ka6LTmOG53qsGIYjJWJ5Xp38XnpdCO4Jsc68vOfxBCuQZD/gg/7qsJZuz/FO/tTVzxXCXSxBUwLLB7OPN/tg7hzUTb2TEUptIXzGQzgwAD4UZ4rpWop2uwLHQHLvvqVxEzXiqZBQ5qdmSPRZktppJXV8kGTVj3ZEasbHEFZEUELYrF4GBIsi493U1eL4V5wt+V6iHrXuyo/06k51hwUEz6lmaXcry8hp2O/8joSWzFQrgY/bmGE2YXLHjiS5R7fE/X2Xhd0I91KY04o2X5LkakwBY1ADUsZ0NDa4Zm1QssGYnLaanx4Or+5t2KiSFqtDUt6H5Wa+Wgs5NBJ+U4nxcYoy+PrBJNYjIMNQj5apTH+UCuti5ZSD0kekG3UUfZGwE0p56XtBfo+BNYhDowjZZB4kGy/feon5sBXU3UyjcPgP+wLrPAhhcwcANlmshG5iXwr3vnHQIKLgKIGz25mDkrX2LN6WGLXOUZujUBPBnRFSb/TQxjJqZ15hsqiBGGRbkRK1UFTQNxW18pwK41MSiC/z7ElmRENhELAPQbwXaXrCRThRPqDzRcQhXOA9SH7Awjm4CEfpv916IECxbvT6I3UyEO9zYH9AUoAy8EkxjFi7IwbIwdHNLWXZQI3Yspl1bVxofRHjSz92ZjPJiMdKHCvqoGBc1uboyBMxmKKMIpsI7jAoU+OENPhGC9AnnxQ/UJlU4vooROrPnUkSiU9L7Ho9/snOtJmXZ6QE0Nls6VNIw0+v0bUeJE7rAd9mq8cbFR0SaHOPkwlPOe9LuofW8YQjlkZhk0rRw3fhEEZ/ne1Nl8OqUFpAp+wjTxf6Hw7V8qs/WCe82ZkahYGH68AAfBwIJS8kCJsyN8VgUoVAEdzhoUK1assVvfDIqGUUaLpg4pNRLR+6pC3S9aWlzsLnJPpezUwWp4VWbcPYeJzvb0F0x2hAsXJ1WHR7cX8vEPsk/SMjtxwi3QKy1oo95I08RzFlxpfO75F8e9LqTmtGQeAJv+429eZ/RfONEIOJPcpj2HrUL8DMkafVBaQBG7CcAEDTKlE5VuhmRDgTmYdMym329reqKcdoE9atDUqsK5n0kXwJT+1DGyl5ym8xEPjctM4v+snCgh/UOaPQj0ABU5Xe+QGRfo1qPzBM+vCflhnHp+j2gzUNscpGbopPeArmrdg/bBtf/uRJ4ABblYmh5f9MJ059y0ocQQa2Vz6EOKkxIQvrfOScVEvJgTGW+lpCLHCkbLCxijdjcUS0IlMHn+ppXPhWTJep0lWrO2MmC3CRlRLKrT0N7AJVtAaq1CddRgVN1WU2pPyZKYZSeHJtfaeFaXDoqUs36FeY81i0svLtlna8oSOC07cxKIx1t4eCEnutWm9uMa/4BW2kqznm24OXNhj/rVaz2zLL3zniniA/S8FbP9FXdxThKcWQuMl1CZod7f/Txlt7+ph2PDhhdrXNNj6hnGZTQ6+MDErekaKekuXtZAVCcKdeo3ZdV6o68hMfGYqm2YGoa+GhWB1Iwad/YojYjnQ7Dal7pAKaoiWByrckFmAluVajC0ZJnjX4dcpCE1JQm5SA+FQhjrzKU++eWjotTDP6KsQq5F9Oire6ZrO3UVZ34ICX3JwsV+lkXC6Q5xr0Xj/ySJde35awXPYpClzRkRSzleeCJ+UwShwlKSeIwuxVVOS5u4IBk7Kci5qu2lnY6oOLwmPv7PPJUxWlrYLkPz0N4c10DgF7ghzjxKQ6q9oPvM0in5nYFamwBCeJJ29jpj7Zz+jBWj7ENtipjWBgpt6wPrhdIM/5jPuljXwO8hkILd+T/FYEA9QpCsGDC9JPX9ZMFVax0SpaKcy6INIAZqtllvYXWE45hwMvyo7pvCtZNCTBSPPcXSGk0JxrFYzczS2KayjQBC5rJ4pclC5Q1ZnmfRERRNrXzTEHI2SbB6KvkbEJhvWqxGlM3eAQxg867Zx5eYDL0xXWoRjBD4KBfmbjETXMXp3SyO/qnSGRjsi9hlW3QBkDoAyKrkPbm/loHaiXxwixi7Vye3n3VtCqzkaqrEabTMVWgkvBBueIcBQSD/III7Wj2swUr+6079hVS6QKzXGLcriJnKKeHYgHQwUxQ7OKezRmuOYrSLD9ZfWVzfowxDacPA95jUmVSJPUJEeEMpb2pRhv+dTyY9XP13GX3EvwUIqF7ByYWnb1gWomMH03mTagA4HXFqyKRlyhmKEvfTCvxu3ojhTibgYWVj1JNycg/9VJlsiqNNXWMBBKZMlAW747lmLyW1XyBXe2v/AEXQ0350fSbEBLoI2D6M+ClApFX7RPyny8Z6Ocet9Jtfp6ufL0Q5ksZ0yx1f9fRfmkxDsXn8bQEDjiAjzFYUUZTmr9QAgL6o9at6vQikClfAjT3tZV/E2t/60ebrr8IEvXaoOnB67vSnTGimYVyjIu5xvoMx82ErEcOM/TD61KuVfQ84h2M7Aa49GZVFPU1sKhCgpuk9mKYgmiXJUEd6/uKhDgHPBeMGqOvFMcDweKuuwSSl7rD6/xU8sX0ljwClDG4AWPopjqzqNfQ6b0Uqrcx9s2EWh6sEyhvWOTlxQc1uu0ccK6D3bul+PBvgt59aLfgj38EkT1OHBu1e0XsXMlVKKawDWF3EnKdoTrHmGSlYAkZh/7LXw6OykpIjKHaHJJlMpKzASMcNv6m1i3P49VGe6DtnFdC/MjDbA26VJj0IMA80Ga20WqXVSNBGRTtv06OnjXIXyEzZQlnqs1Ni8/gdX2c6E5ZBwmz8TesYnUnfzxpohXvFhCGzmW82xyhX0XOmVkVdHLD1BDnjNKqJjt9o0NZ/yTOSxpQ1PgZIC64qM7/BrEHwioUAq7mjc8/KDzXKny5sHeyIAKaVLdXKcsThJQucjJDjfsNH+XibnfqsIodwxVjpAXVE5d4jCT3A2NUSmI059EUC5pZII6+oAJXKBfnIbSARq2pLmAIdVFfc7CTUWA0eVYPOqCZ6zkTYSlvUNZbgTiXQ0LavCObD5iVesoJTdFWwhmXfOtfM5jbm/3nqu7yl7aN4EPtGFS0cNPRjOdJlq0Fbzt24mDJp9TCL2Mww+VuBDRpAWGEWjvTbCkPo1qg6VQNVgJlPno1Z2m+rU6xplCUFUrQk1jaoHv5uqJTDKhjU8O11Dx5amvVVhPwHIsMlJQBvFaKh7aSDj9yAhf45AkyOBEfK4i3Ncm5hVd0hh342B2jMLTvpahBC+h6KI0C3fybKgURiLCEMrDhvtKTs//oRe8gUIo+SMtefsCWwgAABAASURBVPgJIZ4qCYQMQ9j/zUH/vgN1n5zyKd8oB/F0jp+gDCT9IypvGZZ4O1SAKWHycj6yXOZ5EEnbIX0aZOFDybllDhtx+oCnGudSl2jKm2qL3O7FCH5pEkQ6kjR8+8JGevl8jPi+b+6jCzQQ/rcPQn/6JL8BGinhAUCXB59QF+wiZkgSIaj7t5SnHHFx4QwE4GY0oeT1nZnHWmWP/EYNlkCbME/beuZ+x2s7dL0lcXKwoZ0MNuLJg0PZ1vxTBEKcDAtOC7GYzZ+WVjRp2VZ3cqX9xEU2TspQgUnLGzQIto7JZaIP90So6KB+yQNrWvKAKnJzBssQGEia3Whht8COMBv8qfrfiLhl664Hy6OZ8QygtpTfkLTdlEKappIac/LHk+bV7yW0yoAmb1Hn/xTuPC6+l3hgimbBJSib8TmSut/onRaI4j3EeJNYdQOc/Abv41P1jW5CMwbFDsppIRTsZWRBYOYnpoynwI0UY3dwj0EzgAkEF2qlzjJeIR112TLprip9VxUqegqt7p+/BmDOscQmfoKRPZXGB2/Uy03bj9ZFZXfIeHMgSRXyAS8dU3oCLwahyu3plgbR/0CB/PGEqeN6iTStJv9jlUyd+X+MeSfO2kEC6omozDtuh7kYY78F0jYJQoX+4yA9TH9afD3V5QRFBZvTHoyyMWISUJBJsTEx1HPjgOmHHwns4K4W/S5GjT0unqDe9FJE20TpqTkOgyRCTYLeM1KlC/iENqM7U3M4ooR/UVmu2BoyKo8Xh2pEBT/4tvAO83FhtqZruf6kFXoe4KymDzFECtAjq8pmxUGqlhIx3/ghTIxUGotw87yWWHMq1Y23fHMRfmPj9ymI17dHdZOUtfSuqMlo+7OZRB4jcZa8FFwtUHYZyvIqF9IB3LUCGRyTXiTcEi+Rbaonjt3XTLET6YS+L2gHj9EMavR3yNJsPMJgkgo9+mKMhuAhM4hSOCU8x/fOY869jv670zbkX0qs33rDhQ/xJGYiD5V5BDsIPEc9pLdDLRimNBaB46VzhYjfY+gMI80QlRmo2JYVN5zHzz+InC9pgXAXhlk6BPvpICnjUJ4LZQzDLsqmMOT8KPakIO2a/n33VuASPFFpS5cNcLT9Ql/UiaI8L1ShETFx6INLNwtmYXOsFhfyGYJV07ZgG5ZiOSg0Q6MhA9Oued+WHUW7NBtxiOcYvFoWvK8h81zSFwr0MhVjsDD2thOytuaqz/wEaswK5sZzyh7V8cwna/CAlUNmyj+SO2RwWtrxQGsapBkS4vnHcFT+Iz5MbLrUzAz3m1TOAW/UkLOH6ZssgXQES1JxJEZA9xavw9WdhkMZ78Y+JNrQEYrwTXqcLjUB6MZ1JrQqyYciiTyvzV/z3l4aPvYDdEqb5Tmi5hQGIKdgcvEH17xjy74/hriji3QIriOPQ9rTwr7YlPe2SuawUGFizAtTdNwuyxwRNU8Dk3KXX+Xv7/WVvp6EfulnvOinFzKofjqpJgaZERJtbTGAnDhbff1Od0gJnvlTfwIh/Aac6Arl9EkeThZFowDF9HDSJoaxjA4J6Lj3roPqR3CHxw5yMaK+3QsKSoECHodHNXromA7gQ8ljBFR8ekICjyiz0a7GxYsgPH3GDDsZS2Ukk7OatVzYrc5zFOcxONphF65DYT7nHVvjWXdZyXRwSe92JmvS2t9IG4reRnFSiXkOhByLsmLP87Stv1T0g+zsls39U68/AaUeeRm623YlKrz8Yf7LgLAk1BbakbhRT/znXuOxtnAz1Dqtvnq/WI8nxcnlGDQ7iPBbQOUkSeMccxYjW1kx+ucY3GnES1Zt2jQcSniHXKC2NcsuNXIzMII6RCiJSQ5hKK9aSl9+qPvy1N7hYyxDSsTkDoE8az8bubOamBNMXcmJ9tK2alX2o57WY4D+s/KWXgEWgOg+eCE1JtYpOQUL0D3L/EgpHSsvy3KOmPQmmKdtqsqmlPbLeCodfNj8yAaDQNMGQBw/dz9o1QsYUFgLCiYSVTqnwhpgAErPVVjnSZzGsGGTZuKE0xJsE4WT/OwNYxiUjDH61cxzILCZG2wKTfQ43KkOhue9nccnpTA1Xl1asbseEbiNiVedk31lyx18Rd3lpADWskbm1XQOFoMntjHin/nD2ty/uZ494puiY5bZqrAeQxe3eMlcCMfzUbj/DkfM0N5mPVYWfuEVAQIvneFREAMCzFCoeJBYdFjapb00WFigvuqP9IK1YI6O1KB+1SNY16xDHyXoGRL7NOZtxy4dMUzU0rUoISOXtGjgYiaHXHLUFi/hRrP2yZNwL0PgX0RTVxT1mtRKYVNJYpyZV0YfVTcriQSOrixmCF5GAhM4q8MiMF0AOuaa89g7lJHTdLxvB+Ib9SjYsSbRQzosM6VwKMS2gc0DjKNpHvp1gMVIJXqiKChEV0W6aF+0pHSY9PgLNOgLvqjiwhIJD8bJCTzgvaJWdE4zqSq2gQMcyu9Pmpntf8Jryq0TONGrKN2lAVTn8D0WBoNJ5iEhV4xu+JA8DXckh2Cnbx24lSss0f1uUA63YAw9qpBRpG/Y5I2njTeXMC4hDcGKi32AHlrmRQD6UMMGd6GlkYDhSXkKjKr3zNL7LDgtBU9kX0zskRDm1UkOgXgHhye6O1nl4/bz7DRr9+lj0Zc43BtnY/HtxTBgREVmPzNFX1I51QvrCxQ2axldr8JmgAeF0TKMmhyWFPmw8eEg9Iw9z8IdJdzluYFKJXooQ9FJpkHZ/VHERAwF9YHExEyb5JdNZTDIPU6fz2GJivsloGfbIPopFhADlnkwWoAmiU6TsqIvRj1UvAoxA5N2lPE8Ys3ILxkUKo8mqnJ69LhUQkhoFNWjDZ5mxkBfY2DzjFgXLercjuaO+dOtTqnR08vu7SQG0igw0jmIuvBFSKMujRe0ZAgMCWja847laU++BHe0zqc1Pt1Ef0wotNN76wY/umP4+zLkEUPGkosLQjw2AQISmc9L8xDofy8B93gviI+adWO89We6sJ83Qbo7DS8NYnDX219lHQIrAGWOva3foTAKZtqI8YxlHi/1/XK9jh1v8hdtwQwoSoyRD2s38UMCSArqG8QpoVwy3AoQkmFPYx3Rl+GOEGtSMGnUDf3kKg5Nm8RhUkgM1Bf6xkpKmIIBauMbt5gVxF/SPh4rvy7JOZ/d+1CChZn1mKTNzzv6H97R9rApx0o8nkZJOIUrAQ+4AktQkJY0BQSkSRi5vAPoPgNEh2xuHcfIaXAHzkME6sjYLF2lrvWtLCaJCyfcp4mZ1CbiyXAoUa+IlyOuH3kAMNQbAA1sKILepAJPw/EOb6pNICm3Dy09my7ZaNH4+XQq3KVlCO5fbD1lS+sMZMtQW0YeblIGQB6rLNtuQ1kV7NLqj+feL6qv6+ff90AV1vVyDaiAEzCT67eoNgraGVDFBSDhDmSUN+KzKH7w+vn3sgxwXk6vgXtq4w2Itmv0rc60oIuvImXjnjJF0SyGJiiDwXRRKjid1J+onfttHJqvyR64dFJ5v/ajso0BKIYNOAblgkf14thxlRwWylxVgdBhfhE8RZw+2lfDPYYS7Pz0ejzcDdZiBGZlUZRPGp0T0XkGg7hrNJTaEO+3fVRc0/fxALf3Mlsd/sxTovkAJNMCP2UMJMDWUQQOX/kE8mq4Z1Ty6NfdQh5OTZuVpmsyAG8urPRuK3k45BEri8odrVzSFw0w7Jo+ygN/9GMQRDzxAE0k0B2wAA9Q8sn0WrmbBsZPq9eR1HYJtfAryBvhrh6G0On1PDDBhia+KVFJnvVemcJslPnYnZIwPUzdsxArzPX+pRGqrunf9cAf//9ZOlwXNkAzQwXEoMHb3bZowtzHjIuQHX4iNzADzFend8DdfbGxKdxTioCL6eZhf5oOnawE6+TFEfgllxNDIw9/tYZJ/9QX+iR+/fy1Hqhe1FezVWy0+IXQorh7QMCgAaMKGRRhT1RiuZjC5ZiE92XsLJR/0+e9cKdT7im5zDNfMbPTNBQGIgyEcYL4iYrjSSwBxoNQ2egXzVnslb9+/hUPKKCL26pvBxB9RpWhJ+6ZgR4AwxUwU5ISGS+mLOo6gUkOzLekd8F9v0OWeRLzDxBjrGdwruVIYWKiPyl8OI2fwhQ0t3HIzUp//Hs9tLFH/mqi4xfesRBQ/ZZyW8IdZQ2rL4tgXVXARlygoQtMoABVFevpOxd1qfTnbHBHG2bxepyDIbBctTXfs1j3L4bCNAXeyE6UISGW0wCKALv59kBzfYTFU39nqvVn+1unPSQQ6F24O75BAnhJbECRgcOgTfV1oFHL6EuvS2lwSjon3LM/gV5PzaPthcdgPEdLUorJZGBBwe4Qyn1DAPGMWX/4UzaV3Z6+WHbSn6Wh85ouwgPsXlb/rcoijxoxKYOr6HeIE/aJT62CDgxgWSBREbEOrZ7zFHblu8n54S6ThsKM1A1onoMJMYFxjqbhPqcDNGtBP8NGnkzAYvyii7q6uTXokbSaK7lMD/A8uql6X36z4tCCaHn9ctQJqa+dU10LYSRQBZ0qCm2rs9D7+5iP5pyTfAzc08KBCTqO+uNicMuIQTMVGp4vYadApyqJlbYLQoQiwkXnNovrSo9DLjRpj76peuJim75VlNmX21aFj4ACYnION2xnuWoCtHxWQQtAZ2vwypdHUnba5yPhnhYMCfqxT1ZArArG1p1Ckfmdbmrjx0fIIWAxHAO/lAWgv+W8Ev/S5h9Nf9ew+h6dR9ItlhNEQklGIXP4WMuCUBau8AqfJpAc4kqtJDl42f7SIeOg5h/0+Xi4p+GDQF+2gF6jNYiDcXrMkoiSfHh4AE7LyBESQrhSoYYc2vAKmoWEDILX9BUeYMVh3el7dECc0ckgEihsUgTJKWQd5T0POwVoyCrmrQsr+gDzY9Nnwd2jiCG0p78fy2IpZ2jf0hyEA7ovxBHC7YouxuIQzkPl2eo/CNRO8eej/+bFfV3Jx3ig6kn0x21hxWlfZiRORIS4ECP6dCS5qpTMpPDF9YdIFs6sYx16YwPQzf0E8qlw7+OJuPM410vGDLMv4TgOJ3FDhGePUCJbmABi8vCqkqT44ER/z2xRK65vi/2+Ty17JWfyAChvy7n3LTg6l6dpYSI6jpmJTiMIEPHLwCleNsS18xh5E6+/hBrN/DzyJXBvw4u5Tpp0gLOwFwqwll9wpSW4JkcZc9KDyLCc4EqKytC4blblZsW9lZAQmHL9zpn99V7CYcsfducr3UVBeds9Eo4MAf6nB7nflxYsqoN6WISoxdRhmnnfwoZ2PZY5rSTxyZ+vhHsb6sBiP+qmxq1tjsu0HpS+PJDRxk+iuJFLUjnLq4syezKF03ohnsWeRHiuZ/b47JWp4rREOUfA3DkXfg2iiIBigBs4vd+QFaxHeWSySwRpUsp8ZBOrQ3T2LWd6YZQdnEq73AXAvZvC0Q1OGbe/yiJCvyfqxcHLwwToybNuhDcP3A0zb6l1y6tZ3urd+ie7blmCF8J2AAAQAElEQVTvebSi9pqe94AcxSp+g99WtaFceK1+ynJbfM5Vi04ylVOgYLalihipAJO7N0vY/ZKwcieH+eXpguDefDEUTqPi91i467HJ4Q5Y8HhzpXGPYIRyYB0+tVpOoohJHQEIfE2OGuimcCSsR6sfPsRkyYd5Td0DgjiP+z9uV//hn1vdHn12joOrPN98O+XdDvfj3OZ8SYnbwzEvwjenimzQP+BVkbp66+fy4N5HEoM3Ob+X4/2ysN43x+FoPI8QlDwZoB3gm3KuN2IRC13gUdvCwJKvWGqLf5ubUUX6W+7yNXAgblfoN03bQt4cVZr38CregybioeRxq7zKZCAHzbWcfBCgtd4q6ktT8ygDvItLlwv3fVdpvef55n7kib7gVtUJ68a3Chmh8M4noW+a4ZEkgeHS5X2ks6m56q/aqr/SZGDbmvo+hgpnPkJtnbI5zmeMj+kutWojx15c412pX63i2qvwfG+fQFKQjKBs1wH5SsEsCAJQGMpwaa6eBbsUHTZMO5YBgctNfwfc039BCLQdHFnvYzuGl3y7PgMzUaF8WnUAuptz522rV6CHZUtcQugfwt0A/bpi2zrrCz+LH9seUHKm5V9AB9l0caOj69DTxapuiuYYfCCIDefoC4dwMKXufjIofZuajdxqxsmVnmHUrzbiuABBD19LRaVgRyVnouJH8xUi+JCGJealaCEf9fTJMjSkvBx64Z+/Ce4Hrhwil3ygX9bL0C5/RACU4/vqiJZ2mECQADqV1EAJG7QxUzJpyrPnYdkri8oJj1DC0QSPbiCStBFSARPtj6UneZXJA9A5LZVIGkAuollYxUJgcezX3xF8Omnl3siq7IJNWvlPD5ocy+r/AlGV0MrI8YzV0BVjJ2se11YPjuHLUXgDtikWUi1aOF1Z+IcstZAvWdTL34NyhpPpr4V7mm+K6wX931r1tdtZjP1YlzhVhXdvk6O1jAjqQnRbjFWSKuThuIWKylNgDQ5Wem9CCtCfccB/W0FV7oIMZWYIC6qW6kcrdGWe6G95sET692BHH2AOa+BTy2lSqdxeDjVggNRu9jDNnpuu/XCplRv9JKYKMtw00KpEO9QqN00qFRiTRwuaw25xyTUYYg58yuGNSlvFBfERJ/+NEGcsU/oX4D4NRhl2O3cxst7fL9lTloXWoTpTkMEZgUeGDLQouvo4uoADnii1YNBooDYRU1UhHchQSc6cbREQE2c3nHuutB2CiVRPwrp/wdlq1SrQqlr0PCh2tSzzEmif+ONdFoC+uS0Lgx6FwFo/Y73TwCgwEuXoLerCV2XQk3lok0eyo7wt56orEfOitWNvo0Lxb4c445/SPwf3aWRkBjY8EQSP99Xs9dllLvRfyYUPNx3vKdjTSk8zg6HA2dXCdZrgEuAjOeihAcWcIcKHKyCs9yQDMVUhBTupGpHzNEhUikO1dlP7iB8i2KpJBHHqmRWTbcmB0pYqzCNPBgHEVKSchplSUi3zgRxtWMK5E8ZiWba6N+pQBS/pXIV6JP+19E/DfT9YgGYO+kdO9HnA0sLPqTBhJrQAQ5KAg5wwoJJ2/wkaaIIVmiCANuEEK+hxkyjCpbNJ2madQlPSJWke0qJeADKaJZO1rNBMkrK/pZnTPPbksRNOtsLgbCuqtoXaHTNR7jIK9MWsxDfP+jz24AqWg7iLGFyLjn86NbjLv//0OB8ObuDGHQrzWqtaYefD/gew6m0uWAQx4CkbAZXMT4AQh0JiXYWCANdyABpOdfQnyQ/QTDvUBpcJiOHm5kBUy2c/IqilQh1gF3XtAZdOKYvmPIFikuphU/BcEviZ55xiMb1ZwrnRkbnjXByVlr1wci7zFI7a4F5++vGLByAevHgs++Dj53MN4Vx6FHkwcTdq7b//xYJX1p4PM8AqaLJq0pcBmpycEqLCFXVFYiycyvpTN1wMUYPPYurHGapIIFUrNEIT4ne1RAGRKWEePasocRTVXZEOUCVKc6pK24IvA3z3p0ztsr7HEi4n8fnDoz+POhzFGtucsP1cdbgPgZu0a+QFGw/+s//5lfKK4y09je3fWFH0ryeQEZy7sQrmO11tZ0cxQZTGDsrtLheNVHIwVbf76FV8ojCr5GBqWYCdE9C19Bq1YLfr6U145D1cdHpDWluNJxhMCiTMY4qO3KOE7/41le+Eb32zbePvbwJgFm7OuHi4z7cceT8cosNdy5hihuOcHE6O3hY+Fsijt/4KUPfZw0i4yT9LQBLrPYk9D1TPc9rxM15B1kgFs9GfgOE7cffUVYsxV0AKNPfuEh3WRi2473qQT/FS9v/XyHa4pB6pRr7wwD0PDl55DvH3SZmQ4/7txWL/LBG48fCm4/u/2zK75WSssl5zY9xW/NhXEPLCc5mXBnciascQFK5IJrUQWaLJbXJTChOAQwOdPd/qdTQTwJsfTQBk/vU5IO/MA18J9Gz3t784lo75KOTJS0c+9rgwWr2TNuIRQ5OcnMWsEoKpKfic8GjpqX8QE0ufXKdnURaCeGyXo3fhwndWSehf/VT9muI+uPXnVPk27bYK3/mfmcqlkQs5/pMzxOlOLhxDNbiX5rL96j2/KwbZGia4Fi3cbTdFnQF6bh//sUnqb+A37JkwsarNP/wZ8GDR/046HBukXFpxQRQt5EUBoIRk0iA3xaa2yZATQ1XIx4BITwQbFiVO3KH7Cz/Ffyy1bXfVWwug9UO/pqg33CAtwQ32NGTcKyh2QOM3fAuljgyUfLpUFJB3uONK3aCpJixoSdp00c5JbQ4DkxzEnCESJG4lmMVrkZkeEXwTYCasdAfYVL30tq4LI68wh4EoMUZerPIAtLjlqRTH8eTzQEvgRbHkeiMbR7XForsRTlV1k9TEQFKN2F7uPzLppVJRF77B6u+22J7i5M3f7VLhgSGQGAvJr4r1ahn3so9gsJsaBjdumWDtPE7Ce/jT2OMKhrWyZFEBQUI8XUK3wdI3M+LM1cKKUkuIKR6hqISE4HXqq6oJT9NuFgRh2tBWeXZA2NpesLMFYgCeAzVDxfA2/T5wsRshllUSdmItQ2CP6AwQZ4SME7fgiQbffYDOcQ7eqFOQ8AaSUDdULfmCiD6IkaMGEbQWlqLQ/YGiEzY0sXC1/sKIWVeABVOOiYdV3lgWbLg8ZwrWDGHjrTZ2Yi0240zwQJ5nSqoAt5GdbmGYdl3FKT0PtCjhEDH0kU/kSUehVXEBxqpBsO1tykO4x2xULT4vKOVCKzNE0MxFHMd1VwzNp0kYvmRQ0PmTKTSntmlmlSJUmgZMADBEwKD/6c8LdP/CHdwiNqxbtGJTBP2c5L7ol4QNuo3eVmzT1wm5O63KJs1gjMIc46nNm+KorkVLWW3xcQS+UQkBcvve2OdUxxXnoJY8kjXDo6b+4DEpo6ZdUNUWmjQjNrUuVgWbARCHErmgMIrJk0wDq/pIIgcK2RhDonegzFZEW202JDKvshtZsMatNP5mCgNhOIyNoUBr90bLWyrFobgIR1FFExqSh4kIVM3JgfVJA6B30dvOg9V9EKt6E9lcqgva6R4lTV3HMUyq1Fk0scxjxIEprm1mkZcs9Vihjsxw0f91CQelpFpwB+hnJvCs7UeC3Y4ID/7EWUo6Ic1YQr1yNM5e3pNqJ5xFi3HGWjlm1exSSHjyZutFSHi6Z9atZINvox42g8VKhpYDaQN31TQEyfD6Ak/t0kKSRVNCmfRtp3DUhPbEBplsRR4OzwPMluRAMZuYyWcU5DdcTU6CvWHmoRiFqWx7PGp7UmNkAjANmAMkxpsJZ5J5QHEvnJOo96gIM8dQC6wJVnZE7Ljt0Dvvlbe6EWFuN1UWMhZs7Rxn5SUsxyd4hgE2MRoydtxChla9CWIIExFRM5uSLsZVGrKtnOlb5W7vTn25o6emAllExUSh+km+7ECxu0eEevgJAorUwEkZ+OSTQx4ZKLqSIpOZtHvXlk5doCFXNNhZrJqbjN/Ka5gQWXEojuY+CMXLRC45s1stcs7rXm/Xc0S1n683TKp8qEftirUzdEyuHpnP7huDMTIpbqmqw3wsknfhI0XBbAT9NI8e7SVgO8XdWHWAOEnmkKHZSvxEvxwsJXTgju5GK+hE/4MVwrtWpYEeDnyJpR7ikg5EYWYYTq/SJhgLK3uGjUZdBMdaWW4pOi/Owl9E40axsKvhP8mpWjgQyHVhu8IUGwTBJEoMR4MlV2Uw+eRAK0JpG6JFY8fJXJIi4EaqsyDjkVDLU3I1UaAJNDWTN9ut7ApxYBUObcXc37ujYzaiT2pdB6PnzS47E6UCkyQ2dWYe+tUsu2+tkPLAuO44aKbBnk2pHLobsKUthbT8hfashTZJ9YbiRJvpHqfJoMda9lslj5bKuHYSJsPYNASrQiD7VUaGiEstA0/+RM0BPWjtaVwvaWb96r2zlTffxNzJFRylazUyE8LSLowedEpHGCAj0x5oerh3pHZqQYUuEtYVS3WhdwRgoocMNoi6rXRS9lSR2B5McctjDvKI05zUFHogCJfYAUa1fDAHaXeEqpShRA2UGjLJTIpC9ENlZ1qCBEo6pSoFYGTzVsQbkxgVrDtIkA5X96HEHGakaHaAtFwEW2Dat+NxHg7DwKlpH32TRxuNpQYj0Dlpg0tHVIT8kmKinUNzskiJmW3JWUNjkk9OUrgo3KNmq9wye5HAU2lkGkxfTQbzbA+cqfd9SeQZJrXSIN0MUb0iA0ebMQBqvslQxm2u8chNbdFAdwgkVUet00U82LWzQbKQZEpRF3YFbUkwXYk5lJoZdNSMcR0y1MGBjwHQibPTZp0pk5SmKZYytIKDHhKcSUZFPuoZ42Req0Iab+9VMWSsNFtcimkMTPKwsiqZ5OHIAIeYHilOTGVQrgtsTDvoOg2AqhXj4rhdUv4cwh0WL89lu3qVkqZLBjke2UXaIRmsoZElEZ04KZaUjrMqlcBUc3WiltlEtHOavIsII5TyZNoAXEURT4mTvUP3LKRh6643hoM8TGXUeBebLkK9KiimDJQ8LDJQ2koiHc3AcSVc+oWSN4ds4RbvSydDsGAniHvbg/Emk/06E2Nah7IxM4el3XlskDGhpQEzlM+us9+kcKiYjDFTLtrnILOv0DIECB5diCani2U4RA/dvs/BMxrR1DVaUhiNOTpXqRdbgv2ukVzWwKEWJagiD5M6ZMhj/35fYqKcS9pp/WrVDU55KBrEjztkySs9hDu3Ubqi/lAXDKRF+WQHlOmVPszBLNrBg2I0potDAQGLUZWCmRHtXWgwzstEu0OcBw1RRaRpZm2oIgtPlIKb06m6tgB85ZPfOcgji2FITl2kpP1iJLlfmMmRSb05CsWcilYnDoYpz+tVXnnmF+tRsJ+G4EWs0DwP7+bTAClnvLqjrsc49h8PEY7x3l+AYdXnlap0agiTkTDQ4GGmNo2LYhdIprqbOLTHWo+CLN5IGfMQlFzjwDpUDr/pN39qix5ksSVpuAzdOUdarRzbXIskLehlTgAAEABJREFUV5qgEz2TJK2QS3q0L2p3bT0KOMjDRJtot428v9mhF0pUKT2EO7zQfxGMBdhBAzH8mQyiKjtIOvHpcsexHRqPoaAMShjzNFqz6AJtolS5CRoaZ68hZkzKESCvTt3EWkVQkt7J5vv55CBEn6giAyWvTOY8gdGMpJh8UG4DkoMwgrDJiEOBWsosybirrJcNlDxiDpJR1ePPYNDz8n+7DNLaP1MhNC+B9WPxHWcerPrMByZMYWLMZaprw1Tm6KPpih+wED4MKtMPUDgq8kk/R0lJeZKxdA+E82igC5qkkp0kbrEGOOhEJgXgwaEVdJ+PBmSkE4ls2/ulKtumPEVEoJM9WRSdMEPBxqMQta0hbZLpWkqplpLzRIRsT8fgfjcGr/T0aEiDFERF5qH7BjV+dxZF5JHZH7mMg2ubkk9JMnC45GDId3dM+qeGSNEklYtmd24Cn1ox7cd0AUWYVE2q6BcmnORDs0oZuKii2hqQnGImA9I8ekwx0fZHnMsRyIJd3LW3fkjgxc9QgllBq+FF0UOBIQLoe3YJ+hx0zrE2wKjlAsrHNsPPsUyUISMJUJKmr2hBohF8JCVDGYdAo08J8o5ONhF1ETaqaKKGFNyq9duLqsJ7dGCr6EXNnW+S9jyEFlAUIiNqbWJ2M9BBEYpYZqDZe6qiIVUI7Pi4i8KUjsBdddrBo6JZ1sfWVEuAUYjbZLplWJkySalFLvNQamWQzcEs1DiLCOzu2e4aqlKGhimRzZWfukMiCgJTVfY4tW18epKxWvxojjwUGdhWwLUgKf4jzZKUEOeJoBOcsVcB4lpiowxq+WWfwUs+t4j7JbeXYLczn2zBD1PsYDICXBxhD0xjpAK3JBOaRSj5HoVUQkOak0dtOoR8cqBZO1H19aALdE74pkeKUHNonqp2zWlvA7KjpCmTlNbEDqlsSx7O46IUlu1I3X46Dvdgd88q0iA4aZSKQyux4IELUlgUE2y38gyPXt12kmckshi+a1FFMbugyq1Vl5ys3TFVo2ZgNPXDIK+GFspekpMCYpMjkIg6ieMMpOXDQy66s5XaVnH/2sQO4uhA/rISa5h2O8xGtkZMSK36I0PCQ5jrIacD5UyYtj6dAxUTGUtOYvCRMg93yCFyKSyV7KXJV8mkuwy326AzNcCmHrVqTpWb7zg2RjLGhgBAXTLhWiEMt1On6KHoGgmlTjqiO/iIUZUZ/dqwbqGU9tJxuCMQ67GwYJDDBlF0cUFd9iFaQJdrxT2wRpI0sBOpVJGPHSSLGRtFj1yGIvGoitaIUJNU3SHjJslJKrF0Sta6R2zKhtRmBuEp3wxA3nUmMp7B8Oq+AJ1xrb11fsM2eAAdaIuGvyQNu1VfGx7fiDiMY5wMA893ypURiU5MBxTmBCDyEkhf4WfKKUPeCk3EDeRwfg8QIRAnhU2RRA7aQqkcUvBwvCTgKzRdg5qjkI4kYsluBpK0wUgoFUju51mnCkdhzH83PCBPwh0pGoxbbpRs5elAprh7ajBVNEe4ZxBiWDDRXRMaTsNwBhPTUGiKQdWQgVstRarohQQDtRRhSiaHjSR1TgikSajNke84UyyzVdKpbczGMi/MbTlIf7anYxAdGg5W/LeTIYK7NIj3n2UxzFiMjI5Rd7cUwhFttu+c5hzeTp9PNIg1jjYlDz/pTtKORYR4ZSBE6cL8Ju+i+k3moyKdZ60oyKHc6b5a2BLwBzPUEYPlUZ51ijHCf5yeg7ukhxLs4/WLRfmnDFH0PjZUJR/lOOksR6JxpvX2pqCZReTTpy5mcwnvicEUx65kVGpLE8vTWlV4h0sXINv45JA0ZcxpzKRBbD60barmjChiTRpHbv2/x/bXSXMMQOE/nYA+D9ZCP2N3QL3tcUxz4OkEO6y0EBAjew+Byb2IpQycydXIP8RDwtTNJd9jh2Rr5aCgreFHQmTpinrTbGIxynQXSKMWjjLecAaj2P5SNNejEI/gE+kluO81Q5GWB68TPARoOfRS8chZmIGxOSTaU/QoPIxoTmx22xHIPHATosmBSs+hGPKkVAulL7QlTV9Q6x6ZmTONf8QdOKJ5ROs3c/ipBYDG3yQpoA39Pkhl068dLB4bK4/mJDAl1+Nk+7M09wJBseWm5GQtVMGyNIEjiGQRgg/NPDSLChnqOx4QgE8tcUwlTSA7amIGd3E0Rzac90sWcmGS08YBDS+nV8B9X1kMAVzY7dCZuqRjnoK3I3OgYA2b/rlO+PVKRWea6ZSkjEqOYGQsG6Y5wnSQavFCabOijdxdU4U42dSTrYrOTNML3IXodxHYMG5/lftRhmnxHsvdSGjLaR6hg2+ahsBLcRfBaQ+P5iQCSlgprvM3x0NBn7M5HoMgHcwHfAaPoCRMyRMvihnrZIpTSsY0kCBPs5b8Eo1ouosojuZIv/S+HXlNMepW7KUqo/mmu/Eb4d5M3L8MEdMcwCBWU+4DuAyKocyH+7FslyOnBziRVYRheDABRhHmRrEYQynKQj9xKj7FtYogWGdtiG1HghFo2C7jnjvyUi9f6IUqEv0y0XHEgKOjXP+90wMEdNAcEATxLR5WYk0d4x5KCJbjvbHIrNh6sVOInVkvHbWWJ2qEXhvr9dgeoLc0VJKGro1oItmSQ8kMLDLjnSNpzc8H96bwmUvEUHCcrJ+HhmEa+JEM9C6Uf5BhluepKDLCsRu28V8B/Yy3P60qytD/9ooYERrCROaQTuFOAKjIREKYxNL0WcZ+Jtw/a0zXfq4eeMIDV7g/4Zgr+1/0wNfC/V/06HVMF+yBK9wvODhX087tgSvcz+3Rq74L9sAV7hccnKtp5/bAFe7n9uhV3wV74Ar3Cw7O20y7tnraA1e4P+2ba80/54Er3P+qkP6p9U8tpPdb/aecTdWeMbX4p0d+rupGP7q0V3MR2UuHO17b/bTdz9VzkSZ+m7oTJv8GWLyhycfHsTnhh3/RfLZakf671Q8JyiFv6b7+rKub24Ke2QqPvUXFsTbYWX7clhv/PNvNii7qTf7y+jHpr+BdLtzxXfWPpBb/LJuKZA5/owuPsUQRMNy68m/lVWQ2qwLWcTSx/HFLQ8ReTNJjPOnXifd+QVd8tHmtQhVFplxFoC+0YlpAP0b384Sld2rI1ELPS5YxNP08IOPa6sslLJ/+/m2JrX5cX1XoeUnJfj0Gl8Vt2XbeI5f2itdd5Zkb/fxgLYGF2FmwF7+9Ts3HSl8o3EFwwXdyWNQi1+HBKL7/PnAImAYKm4oAclA1ajK1ggn0vAh6IDhbJQJoUrZoairKTQVSGMNaBa1eEctst9ACR/FZLJFc+FdCj4LYN58VxmBwU9LWPwGl93bkKjQDILCDI2yYvyuLMyTMALFcMiqd8gmaz8dSKrpwF1RDO2rzKepShuasL8oTCOy0wTP9wah4F/N5M9w/cARefggGgVAvsRj9VdJlWZNZlv1/wLSjuy0qs3FcRFlE+Hv2yCqirGS67zeFMB+k1Q1BokcgJRnaNgH065c+mXIwNN18aZKIojy5UZBBSX43EKmDBKCZM0yM2OiHnmkC2iSBYZvKFNKQVT72uRuRZ867u8AV4e9UF0EWedjaLpM7NQ0l1hGtedAqNmh4166jMs+ZeAUHRlnHuNV3g7Ez7kb0X066SLgDTXlIKwQQl8v8hdKY+7umquqfIWI7Fv2dQTUrCKT+mONulK/XI8H0NCis2UIVi5DlHpAYYCDblqWib6XCMXZn4JgoUqQLySimpUmiXFyWMaWxLCLWI6IHiaWXRX0rJcgzQ9SkpNrqfNX94Yn7PqPWX8moNZ0WfYHW2oNZrYxNeqKt6o9/AjvRXKwSWhf1uSl3XMnEVVvbUQs+ZyINU9VlZS4O7jg9tE54pQQ9QPxZjwXQnAOdwN211NhybQ2CSWLwiU9IYbOthz5OazQAKLD3qI6lVH+IsBy3v8p2HLf5i75Ncrxvf2LC7Bp/j5qZDxT8KdrACOtG9ryU9VJ/mMP6h23sK2SYei9P2VYwTKgMRsek6vqZwAyVoXXGq6+xGKsNaD0wJ189bQr/6o28gSVRdFOFc7Hp4uDOU6YAUISAYJ04xXNDAAVcjrvrjOteGyNefIVUi5D+D7e9+swiEN78GEDJaxSOFvuBlb5oag2lSwq+0toEj18qIN5q6mpdlzHLyAmMHjK/l2jD+GDMG5t3VM2QiMcnsatHngmgGmzb4+8kXsoNRX/fOE8xadAjE/eiZLyCyufhkCn3ioafLXpxcK+KouALDspwujscLcLPbviwUcyLNwMskFFU+0REVEXLytaIy3PJVgm+e2vtcXkeTxdgHZhqkgTL+aFclMINAVXYFAD3icW1/kEDekr0/3APLxXhEj7N6rTDOVR/Wmk+uvcquuVexPW0hpOU/kPM1io2E/cSMxcGd4VQcQUBWlNP9JhgJ3eDGJD9qFGwKlfQDraKzmoeCYhBQ8BHv1CVn/n8YTZSXV+0sOqExzCi96ce2ljj9eyBRK0M/9jTBSjX0OgTbPP0zBkIGw9tkMQq87HdMVx6A2HIDLw13HK4dHv0HtgEHl90f0AHFXXF3YzrpabLgrv3o1qx5C6BWNcXP4YCEDSw2iJ90MhoQABIhRfFg9osEC5mTNLkPEVrW2KRfUqk83U8mmIRTw+H2egGERjflJsxEa3uFCo7vRXnmJvK7EWvKI83j24aiL4i8QbUC4GbyAd1w4n+Kw5q7F63Zu/Oc9cT96iU+Fp6WXAHi1X+0AJPaDm520v6/5iOrjqKOntffA09hip0But6Cyo4UR+PPswHYMT6+ajmkBG6d8NCK/TZxErM/iqt4pH6Kdk585B+1TtQOyalvjyrqbRzEJ9z3veLvRCsNydtiphjah/eawVZ+Wqj99PkT0pDxDwFqwxtB2vJuSx6YXAXInGQnM5Kz3Me8UhaNjobBtlUP0iJg0hAt+A9EAFPgVJu2TE8rMoymqlV/gkBVfnD6l5lJ/pcfpowhCi6WT3VaTZFxhkpfOYmwKxBDGH37i/PaLME7+1Jz6b4BgXcJeYhxGu9kCWFo3ReElN1SmoPAG7IAs+u7JRWny5zYXDHU0KSFgngSxb/EWAocIzFst/3H/oJYcAqMUXrcS0cQCKaF3IPkjV74WyL94P6XZHVXR0lSnbsIzmLwa/lWZ02yUQ6aUSTwzRkcapCWI/dOuJkH/9WbIH1kMO1ELS7xDzG9WjthCD08mhz0q6G/QxJMdKkrOVMX0zIYZ+RXhjcAXgh5o5rPoHpZ5Wi+H1q3Jn/aPR4uWGdncPeufskWAWI1rZdprop02Xq0d3zJKYMUGAzEeXY1FJ9/2CYuwOaQKhzH1//SJuFdSt4XM/JjOdzAVJlO8YMRHpmFp1d5m7+casXOGy0eLUkoYp7dc3PEFrjsUixqPVGXWTNC5SbQ5H9AdX2/dkhv6DrnNX7ui4O7o46FlZCi98D0N+N5J85awNSJDeM+uDcHU0kHWIIo4pge7EC90GKBilH+qkunvUAAAZTSURBVEHdftFTK7Xts4/kJ1wS+arpdETGLOq5MojdUSPlKdkwzBODu1DwPmu9LDrPcZNS9A2FH89+XVRNDz7VCzDtQeeDxySKKLc09aVwCnTCdtwxku8q6xUmbazgwsiFwd0hJPjE4Fl8HHiRLTJNBGXYx/budVON0aKd8YDQkVRZKUtCysqOiDRWbKWtFZ6/qC8WPK/EhtdR8bpAoWU4lBRgHkphELirwGjWqsBWgHjJUwkzOPTUMn8CLpGWQ3RqRL8o9fq90TfU8zFJte3VmKyi34rxWrBp+mza7eCr5syzsl9SeWFwHwir/FCJwjHgqu7RJ9t4CTSgDwUIXgpIZ9d/KKJSGOvIsHNQ+emP8SUcPC3SagAlyxya1WTjh8tWs7uAMMxrMoLvrmrKhXbYzAM2RROPN6lFdz9Arzkge+QBZs4PAXdP7lhWswKj6FlqubAcIIcZpmK6mrkqBgJ6TlArik8mjVfGIPDkgS91X5guDO6gg/23/BGnLw8ODPODtZm3SIRG7Xcf1i2t/JKK9rWqXeVerkoC0A97vMdZ70mC7SkdgorHAvscNk4kcaS8zB7uN5iKhc1xsa55EVwk/PCDYWbVvsdwyYQm8XvJlg8ZICvEc1zz7PZDZ7va3QnKseawfyxbfRdo5KlAGYrL6JmRZyd1hHoO418+nYwBtZp73HLV7sI+lwV3BU9IAkfCB4E5xV0AXNHI3cjM2d4MDZxkWyBQ/tx70EFSbmzSNTy86p4j20B82bx0ajGU/njtqViK9hvGYv1Z9XcknKuoA+GjPPMFIe3xmBKHq7satg/LfMdlmFXrourPnR7tQDTBxKwMMnT4OOITMFoGbhdBnhQ9rwzPTuuRiYRaVOusBpuPvfpFQGnOSEH8kdusar/6c1lwlzfaAoxvfdCu2Ij9zIddvqQLjtYXfSXJscPGeOo7VHbtsRjLc/8EgNTznNQcETqqSLOAcZZX3Fd5AgEBiNUElTQUrNm9FLYcnGqzDMNW0hKr2aj8ow+ad5KPaicGuPR3oc2grxI8YzC1SJMPMZWi7nV6y9sOH93gGYJho4KiIdOUCVMXu78RU5FNztTFpta8P2v5eEbr11RdHNwVg7b/AxxRCU/+LdKGvW8BWw/99IdZAfZgV11ublf/+U+Nbm6Bo27uTAMAx5t2Fi2knkyAmBX0WBeHTULfgEdYvQFcFmzOLlazW2bdoWArxXqMtiUQCoUYAyK4hyHCyg1MnwZH3XIPoaG7s4E0OppiCG1sFlpcLeBWm6pzG3zCnp6F2V2DyOduJm58QO7G4KWH24ovnau222SvuKja2dPFf0yDFeOSrfhcopf1uTi4457xbqyAYNrV8KAGdsF9/snctJAgWljO2x/dASOHV0QfUE7tfOS9SbBDfRpPViOiIIGnlyTR5j00ndBKjfjo7vF0Q9b42IIYzkkT4yEN3PeZCey8n25IB2WjJmwn1B8rvVjPfVgvNOQZI6GhoG/8VS3205Z9Fn2X9Zyq/TrJz9nVoLNijKraqiS7vKyI1/piaFe4yx+nfOZBwPpBe3ozwwauHv65Kmstd1tPD8JAMOhAYAruv3o5NVqPlFDxXJqrMlDwYpwGzFuWOaJASpr1OaGVgAi4t8vxfqllGKy/2IpJzEAspsE/PzE0An9Am5XTJEq6JQocbjJUAdOnvp7p1k8R3aY0i4LxkmeXjyTOh2ImNPsiH9hM+fLSJa7u8tIQOHS8HxUkgk2QREeYgEYC02ewJDC6/zWyK9jqkEFguht7JCbR5zLB3pcgLU5rNZTgBJC+1nQ3BvA9HUDDc2YcqcsB3i/xBsM/InCU5VaS52iIWyVYn4fGSAZfzeNooxeZOBYna7yThnnAKXrqDVYWfM5kzpnworbPF7hUuDdPEKEgZrs0ebkJHF6IMevfa/HUdTCR4onvKXSRg2vQF/ZAD9gfV3g1RgGfAPqbe9Gr2z45jMfjxe0sLkyk9ZJIPdnw9RVnb3HhcD/7eK8Kv7UHrnD/1uH/boO/wv27Rfxbj/cK928d/u82+Cvcv1vEv/V4r3Av5VsD4HsN/gr37xXvbz7aK9y/OQC+1/CvcP9e8f7mo73C/ZsD4HsN/wr37xXvTxvtZXZ0hftlxuVq1Yd44Ar3D3HrVelleuAK98uMy9WqD/HA/wMAAP//0h72iQAAAAZJREFUAwDWiMZubdH7hAAAAABJRU5ErkJggg==">'
        #    ,"Vergara E Riba")
        #calcular_recomendacao_livro(current_user)
        #atualizar_precos(db.session.query(Livro).filter_by().all())


app.run(debug=True, host="0.0.0.0", port=144)

#finalizar_crawler_drivers()
print("fim")
