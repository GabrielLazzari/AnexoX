import hashlib
import os

from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from unidecode import unidecode
from werkzeug.utils import secure_filename

from python.banco import db
from python.crawler import finalizar_crawler_drivers
from python.modelos.usuario import *
from python.modelos.livro import *
from python.modelos.publicacao import *
from python.pesquisa import processar_filtros

app = Flask(__name__, static_folder='templates/static')
app.secret_key = 'ola'
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste_sql_alchemy.db'
app.config['UPLOAD_FOLDER'] = 'templates\\static\\imagens\\usuarios'
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()


@lm.user_loader
def user_loader(id):
    return db.session.query(Usuario).filter_by(id=id).first()


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    pagina_solicitada = unidecode(request.args.get("pagina", "usuario").lower())

    print(request.method)

    if request.method == "GET":
        return render_template("login.html", pagina=request.args.get("pagina"), nome="", senha="")
    elif request.method == "POST":
        nome = request.form['campoNome']
        senha = request.form['campoSenha']

        usuario = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not usuario:
            return render_template("login.html", erro="Nome ou senha incorretos",
                                   pagina=request.args.get("pagina"), nome=nome, senha=senha)

        login_user(usuario)
        return redirect(url_for(pagina_solicitada))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    pagina_solicitada = unidecode(request.args.get("pagina", "usuario").lower())

    print(request.form)
    if request.method == "GET":
        usuario = Usuario()
        if current_user.is_authenticated:
            usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
        return render_template("cadastro.html", usuario=usuario.dicionario(), editando_usuario=current_user.is_authenticated)

    elif request.method == "POST":
        if current_user.is_authenticated:
            novo_usuario = db.session.query(Usuario).filter_by(id=current_user.id).first()
            novo_usuario.nome = request.form['campoNome']
            novo_usuario.email = request.form['campoEmail']
            novo_usuario.cnpj = request.form['campoCnpj']
            novo_usuario.tipo = TipoUsuario(int(request.form['tipoUsuario']))
        else:
            novo_usuario = Usuario(
                nome=request.form['campoNome'],
                senha=request.form['campoSenha'],
                senha_confirmar=request.form['campoConfirmarSenha'],
                email=request.form['campoEmail'],
                cnpj=request.form['campoCnpj'],
                tipo=TipoUsuario(int(request.form['tipoUsuario'])),
            )

        print(novo_usuario.__dict__)

        if (msg_erro := novo_usuario.validar_campos()) != "":
            return render_template("cadastro.html", erro=msg_erro, usuario=novo_usuario.dicionario(), editando_usuario=current_user.is_authenticated)

        if not current_user.is_authenticated:
            usuario = db.session.query(Usuario).filter_by(nome=novo_usuario.nome, senha=hash(novo_usuario.senha)).first()
            if usuario:
                return render_template("cadastro.html", erro="Um usuário já existe cadastrado com esse nome", usuario=novo_usuario.dicionario(), editando_usuario=current_user.is_authenticated)

            novo_usuario.senha = hash(novo_usuario.senha)
            db.session.add(novo_usuario)

        db.session.commit()
        novo_usuario.atualizar_caminho_imagem(request.files.get('imagem', ''), app.config['UPLOAD_FOLDER'])
        novo_usuario.atualizar_preferencias(request.form.get('campoPreferenciasLiterarias', "").split(";"))

        login_user(novo_usuario)

        return redirect(url_for(pagina_solicitada))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("inicio"))


@app.route('/pesquisa', methods=['POST', 'GET'])
def pesquisa():
    filtros = request.form.to_dict()
    print('pesquisa', filtros)
    if len(filtros) == 0:
        filtros = request.get_json()
        print(filtros)
    else:
        for chave, valor in filtros.items():
            if valor.lower() == 'true':
                filtros[chave] = True
            elif valor.lower() == 'false':
                filtros[chave] = False

    if filtros.get('primeiroretorno', True):
        print('Primeiro retorno')
        filtros['qtdItens'] = processar_filtros(filtros, retornar_quantidade=True)
        return render_template('pesquisa.html', filtros=filtros)
    else:
        print('Segundo retorno')
        retorno = processar_filtros(filtros)
        retorno = [r.dicionario() for r in retorno]
        print(filtros['limit'], filtros['skip'])
        #print(retorno)
        return jsonify(retorno)


@app.route('/sugestaoPesquisa', methods=['GET', 'POST'])
def sugestao_pesquisa_livros():
    dados = request.get_json()
    print('sugestao', dados)

    livros = Livro.query.filter(Livro.titulo.ilike(f"%{dados['valor']}%")).order_by(Livro.titulo.desc()).limit(3).all()
    usuarios = Usuario.query.filter(Usuario.nome.ilike(f"%{dados['valor']}%")).order_by(Usuario.nome.desc()).limit(3).all()

    print(usuarios)

    a = {
        'pesquisa': [],
        'livros': [livro.dicionario() for livro in livros],
        'usuarios': [usuario.dicionario() for usuario in usuarios]
    }

    print(a)

    return jsonify(a)


@app.route('/usuario', methods=['GET', 'POST'])
def usuario():

    id_usuario = request.args.get('id', '0')

    print("id", id_usuario)
    usuario_tela_logado = False

    print('usuario_atual', current_user, 'autenticado:', current_user.is_authenticated, 'anonimo:', current_user.is_anonymous)

    if id_usuario == '0' or (current_user.is_authenticated and int(id_usuario) == current_user.id):
        if not current_user.is_authenticated:
            return redirect(url_for("login", pagina="Usuário"))

        usuario = current_user
        usuario_tela_logado = True

    else:
        usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
        if not usuario:
            #flash("Usuário não encontrado", "error")
            return redirect(url_for("pesquisa"))

    usuario.usuario_tela_logado = usuario_tela_logado

    return render_template('usuario.html', usuario=usuario.dicionario(usuario_tela_logado=usuario_tela_logado))


@app.route('/excluirUsuario', methods=['GET', 'POST'])
def excluir_usuario():
    id_usuario = request.args.get('id', '0')

    usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for("inicio"))


@app.route('/seguirUsuario', methods=['GET', 'POST'])
def seguir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    if (msg_erro := current_user.seguir_usuario(valores['idUsuarioSeguir'])) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/deixarSeguirUsuario', methods=['GET', 'POST'])
def deixar_seguir_usuario():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    if (msg_erro := current_user.deixar_seguir_usuario(valores['idUsuarioDeixarSeguir'])) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/retornarUsuariosSeguindo', methods=['GET', 'POST'])
def retornar_usuarios_seguindo():
    pass


@app.route('/retornarUsuariosSeguidores', methods=['GET', 'POST'])
def retornar_usuarios_seguidores():
    pass


@app.route('/livro', methods=['GET', 'POST'])
def livro():
    id_livro = request.args.get('id', '0')

    print("id", id_livro)

    # Tentar buscar o livro no banco de dados
    livro_db = None
    if id_livro and id_livro != '0':
        try:
            livro_db = db.session.query(Livro).filter_by(id=int(id_livro)).first()
        except:
            pass

    # Se encontrou o livro no banco, usar os dados reais
    if livro_db:
        livro_dados = livro_db.dicionario()
    else:
        # Dados de exemplo para demonstração
        livro_dados = {
            'id': id_livro,
            'titulo': 'Senhora',
            'autor': 'José de Alencar',
            'editora': 'Saraiva',
            'data_publicacao': '01/01/1875',
            'estilo': 'Romance',
            'numero': '1',
            'descricao': 'Senhora é um romance urbano de José de Alencar, publicado em 1875. A obra retrata a sociedade fluminense do século XIX, focando na história de Aurélia Camargo, uma moça que usa sua herança para comprar um marido, Fernando Seixas, como forma de vingança.',
            'imagem': 'Senhora.png'
        }
    
    # Comentários de exemplo (aqui você pode implementar um modelo de comentários)
    comentarios_exemplo = [
        {
            'id': 1,
            'texto': 'Excelente livro! A narrativa é envolvente e retrata muito bem a sociedade da época.',
            'usuario': {
                'nome': 'Ana Silva',
                'avatar': 'default.jpg'
            }
        },
        {
            'id': 2,
            'texto': 'Um clássico da literatura brasileira que todos deveriam ler. A crítica social é muito atual.',
            'usuario': {
                'nome': 'Carlos Santos',
                'avatar': 'default.jpg'
            }
        }
    ]

    return render_template('livro.html', livro=livro_dados, comentarios=comentarios_exemplo)


@app.route('/retornarListasLivro', methods=['GET', 'POST'])
def retornar_listas_livro():    
    valores = request.get_json()
    id_usuario = int(valores.get('idUsuario', 0))
    id_usuario_atual = 0
    if current_user.is_authenticated:
        id_usuario_atual = current_user.id

    if id_usuario == 0 and current_user.is_authenticated:
        id_usuario = current_user.id

    listas = db.session.query(ListaLivro).filter_by(usuario_id=id_usuario).all()
    
    return jsonify({
        'erro': '' if current_user.is_authenticated else 'Deve estar logado para acessar esta funcionalidade.',
        'listas': [{**lista.dicionario(), 'usuario_id': id_usuario_atual} for lista in listas]
    })


@app.route('/retornarListaLivro', methods=['GET', 'POST'])
def retornar_lista_livro():    
    valores = request.get_json()
    usuario_id = int(valores.get('idUsuario', 0))

    lista = db.session.query(ListaLivro).filter_by(id=valores['idLista'], usuario_id=usuario_id).first()
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

    nova_lista = ListaLivro(
        usuario_id=current_user.id,
        nome=valores['nome'].strip(),
        descricao=valores.get('descricao', '').strip(),
        visibilidade = Visibilidade(int(valores.get('visibilidade', 0)))
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
        
    db.session.commit()

    return jsonify({'erro': '', 'lista': lista.dicionario()})


@app.route('/apagarListaLivro', methods=['GET', 'POST'])
def apagar_lista_livro():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=valores.get("idLista", 0), usuario_id=current_user.id).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada ou já excluída'})
    
    db.session.delete(lista)
    db.session.commit()

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


@app.route('/vincularLivroLista', methods=['GET', 'POST'])
def vincular_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idLista']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    if (msg_erro := lista.vincular_livro(valores['idLista'], valores['idLivro'], current_user.id)) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/desvincularLivroLista', methods=['GET', 'POST'])
def desvincular_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idLista']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    if (msg_erro := lista.desvincular_livro(valores['idLivro'])) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/moverLivroLista', methods=['GET', 'POST'])
def mover_livro_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaLivro).filter_by(id=int(valores['idListaAtual']), usuario_id=int(current_user.id)).first()
    if not lista:
        return jsonify({'erro': 'Lista não encontrada'})
    
    if (msg_erro := lista.mover_livro(valores['idLivro'], valores['idListaMover'])) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': ''})


@app.route('/criarPublicacao', methods=['GET', 'POST'])
def criar_publicacao():
    if request.method == "GET":
        return render_template("criarPublicacao.html", publicacao=Publicacao())
    elif request.method == "POST" and current_user.is_authenticated:
        nova_publicacao = Publicacao(
            titulo=request.form['campoTitulo'],
            usuario=current_user
        )

        print(nova_publicacao.__dict__)

        if (msg_erro := nova_publicacao.validar_campos()) != "":
            return render_template("criarPublicacao.html", erro=msg_erro, publicacao=nova_publicacao)

        db.session.add(nova_publicacao)
        db.session.commit()

        return redirect(url_for("usuario"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        #garvar_livros_aux()

app.run(debug=True, host="0.0.0.0", port=144)

finalizar_crawler_drivers()
print("fim")
