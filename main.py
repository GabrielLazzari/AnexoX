import hashlib
import os

from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from unidecode import unidecode
from werkzeug.utils import secure_filename

from python.banco import db
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
        return render_template("cadastro.html", usuario=Usuario())
    elif request.method == "POST":

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
            return render_template("cadastro.html", erro=msg_erro, usuario=novo_usuario)

        usuario = db.session.query(Usuario).filter_by(nome=novo_usuario.nome, senha=hash(novo_usuario.senha)).first()
        if usuario:
            return render_template("cadastro.html", erro="Um usuário já existe cadastrado com esse nome", usuario=novo_usuario)

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


@app.route('/pesquisa', methods=['POST'])
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

    if not filtros.get('qtdItens', False):
        print('Primeiro retorno')
        filtros['qtdItens'] = processar_filtros(filtros, retornar_quantidade=True)
        return render_template('pesquisa.html', dados=filtros)
    else:
        print('Segundo retorno')
        retorno = processar_filtros(filtros)
        retorno = [r.dicionario() for r in retorno]
        print(retorno)
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

    return render_template('usuario.html', usuario=usuario)


@app.route('/excluirUsuario', methods=['GET', 'POST'])
def excluir_usuario():
    id_usuario = request.args.get('id', '0')

    usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for("inicio"))


@app.route('/livro', methods=['GET', 'POST'])
def livro():
    id_livro = request.args.get('id', '0')

    print("id", id_livro)

    return render_template('livro.html')


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
