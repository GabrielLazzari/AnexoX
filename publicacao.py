from datetime import datetime
import json

from flask import Blueprint
from flask import Flask, g, render_template, request, redirect, session, flash, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from sqlalchemy import inspect
from unidecode import unidecode
from werkzeug.utils import secure_filename

from python.banco import db
from python.modelos.comentario import Comentario, OrigemComentario
from python.modelos.livro import Livro
from python.modelos.publicacao import *
from python.modelos.usuario import Usuario

publicacao_bp = Blueprint('publicacao', __name__)


@publicacao_bp.route('/criarPublicacao', methods=['GET', 'POST'])
def criar_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})

    if request.method == "GET":
        valores = request.args
        conteudo_livro = ""
        if "idLivro" in valores:
            livro = db.session.query(Livro).filter_by(id=valores.get("idLivro")).first()
            if livro:
                timestamp = int(datetime.now().timestamp() * 1000)
                conteudo_livro = f"""
                    {{
                        "blocks": [
                            {{
                                "data": {{
                                    "idLivro": {livro.id},
                                    "value": "<div class='livroSelecionadoPublicacao' idlivro='{livro.id}'><div class='areaCabecalho'>                <img class='imgLivro' src='{livro.img.replace("\\", "/")}'>            </div>            <div class='dataContent'>{livro.titulo}</div></div>"
                                }},
                                "id": "{timestamp}",
                                "type": "livro"
                            }}
                        ],
                        "time": {timestamp},
                        "version": "2.31.0"
                    }}
                """
        return render_template("criarPublicacao.html", publicacao=Publicacao(conteudo=conteudo_livro))
    
    elif request.method == "POST" and current_user.is_authenticated:

        valores = request.get_json()

        nova_publicacao = Publicacao(
            conteudo=json.dumps(valores['conteudo']),
            usuario=current_user
        )

        if (msg_erro := nova_publicacao.validar_campos()) != "":
            return render_template("criarPublicacao.html", erro=msg_erro, publicacao=nova_publicacao)

        db.session.add(nova_publicacao)
        db.session.commit()

        return jsonify({'erro': ''})


@publicacao_bp.route('/publicacao', methods=['GET', 'POST'])
def retornar_publicacao():
        
    if request.method == "GET":
        if not current_user.is_authenticated:
            return render_template("publicacao.html", publicacao=Publicacao().dicionario(), erro="Deve estar logado para ver a publicação.")

        id_publicacao = request.args.get('id', '0')

        publicacao = db.session.query(Publicacao).filter_by(id=id_publicacao).first()
        if not publicacao:
            return render_template("publicacao.html", publicacao=Publicacao().dicionario(), erro="A publicação não existe mais ou foi alterada.")
        
        print('idddppp', id_publicacao, publicacao.dicionario())

        return render_template("publicacao.html", publicacao=publicacao.dicionario(), erro="")
    
    elif request.method == "POST":
        if not current_user.is_authenticated:
            return jsonify({'erro': 'Deve estar logado para ver a publicação.'})

        id_publicacao = request.get_json().get('id', '0')
        publicacao = db.session.query(Publicacao).filter_by(id=id_publicacao).first()
        if not publicacao:
            return jsonify({'erro': 'A publicação não existe mais ou foi alterada.'})

        return jsonify({'erro': '', 'publicacao': publicacao.dicionario()})


@publicacao_bp.route('/reagirPublicacao', methods=['GET', 'POST'])
def reagir_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para interagir com a publicação.'})
    
    valores = request.get_json()

    publicacao = db.session.query(Publicacao).filter_by(id=valores['idPublicacao']).first()
    if not publicacao:
        return jsonify({'erro': 'A publicação não existe mais ou foi alterada.'})

    publicacao.reagir(current_user)

    return jsonify({'erro': ''})


@publicacao_bp.route('/salvarPublicacaoLista', methods=['GET', 'POST'])
def vincular_publicacao_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para salvar a publicação.'})
    
    valores = request.get_json()
    lista = db.session.query(ListaPublicacao).filter_by(id=valores["idListaPublicacao"]).first()
    if not lista:
        jsonify({'erro': 'A lista não existe ou foi alterada.'})

    if (msg := lista.vincular_publicacao(valores["idPublicacao"])) != "":
        return jsonify({'erro': msg})
    
    return jsonify({'erro': ''})


@publicacao_bp.route('/excluirPublicacaoDaLista', methods=['GET', 'POST'])
def excluir_publicacao_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para excluir a publicação da lista.'})
    
    valores = request.get_json()
    lista = db.session.query(ListaPublicacao).filter_by(id=valores["idListaPublicacao"]).first()
    if not lista:
        jsonify({'erro': 'A lista não existe ou foi alterada.'})

    if (msg := lista.excluir_publicacao(valores["idPublicacao"])) != "":
        return jsonify({'erro': msg})
    
    return jsonify({'erro': ''})


@publicacao_bp.route('/compartilharPublicacao', methods=['GET', 'POST'])
def compartilhar_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para compartilhar a publicação.'})


@publicacao_bp.route('/excluirPublicacao', methods=['GET', 'POST'])
def excluir_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para excluir a publicação.'})
    
    valores = request.get_json()

    publicacao = db.session.query(Publicacao).filter_by(id=valores['idPublicacao']).first()
    if not publicacao:
        return jsonify({'erro': 'A publicação não existe mais ou foi alterada.'})
    
    if publicacao.usuario_id != current_user.id:
        return jsonify({'erro': 'Você só pode excluir publicações que sejam suas.'})
    
    if (msg_erro := publicacao.excluir()) != "":
        return jsonify({'erro': msg_erro})

    for comentario in db.session.query(Comentario).filter_by(origem=OrigemComentario.Publicacao, origem_id=publicacao.id).all():
        db.session.delete(comentario)

    db.session.delete(publicacao)
    db.session.commit()

    return jsonify({'erro': ''})


@publicacao_bp.route('/retornarListasPublicacao', methods=['GET', 'POST'])
def retornar_listas_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para ver as listas de publicações.'})

    listas = db.session.query(ListaPublicacao).filter_by(usuario_id=current_user.id).all()

    return jsonify({'erro': '', 'listas': [l.dicionario() for l in listas]})


@publicacao_bp.route('/retornarListaPublicacao', methods=['GET', 'POST'])
def retornar_lista_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para ver as listas de publicações.'})

    valores = request.get_json()

    lista = db.session.query(ListaPublicacao).filter_by(id=valores['idListaPublicacao'], usuario_id=current_user.id).first()
    if lista:
        return jsonify(lista.dicionario())

    return jsonify(ListaPublicacao().dicionario())


@publicacao_bp.route('/controleListaPublicacao', methods=['GET', 'POST'])
def controle_lista_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()

    lista = db.session.query(ListaPublicacao).filter_by(id=valores['idLista'], usuario_id=current_user.id).first()
    if not lista:
        lista = ListaPublicacao(
            nome=valores['nomeLista'],
            descricao=valores['descricao'],
            usuario_id=current_user.id
        )
    else:
        lista.nome = valores['nomeLista']
        lista.descricao = valores['descricao']

    if (msg_erro := lista.controle_lista_publicacao()) != "":
        return jsonify({'erro': msg_erro})
    
    return jsonify({'erro': '', 'listaPublicacao': lista.dicionario()})


@publicacao_bp.route('/excluirListaPublicacao', methods=['GET', 'POST'])
def excluir_lista_publicacao():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para acessar esta funcionalidade.'})
    
    valores = request.get_json()
    lista = db.session.query(ListaPublicacao).filter_by(id=valores['idListaPublicacao'], usuario_id=current_user.id).first()
    if not lista:
        return jsonify({'erro': 'A lista não existe ou foi alterada.'})
    
    if (msg_erro := lista.excluir()) != "":
        return jsonify({'erro': msg_erro})

    return jsonify({'erro': ''})


@publicacao_bp.route('/retornarPublicacoesLista', methods=['GET', 'POST'])
def retornar_publicacoes_lista():
    if not current_user.is_authenticated:
        return jsonify({'erro': 'Deve estar logado para ver as listas de publicações.'})
    
    filtros = request.get_json()
    filtros['limit'] = filtros.get('limit', '5')
    filtros['skip'] = filtros.get('skip', '0')

    id_usuario = current_user.id
    usuario = db.session.query(Usuario).filter_by(id=filtros.get("idUsuario")).first()
    if usuario:
        id_usuario = usuario.id

    publicacoes = []
    if filtros.get("idListaPublicacao") == "minhaspublicacoes" or id_usuario != current_user.id:
        publicacoes = db.session.query(Publicacao).filter_by(usuario_id=id_usuario).order_by().limit(filtros['limit']).offset(filtros['skip']).all()
    else:
        lista = db.session.query(ListaPublicacao).filter_by(id=filtros['idListaPublicacao'], usuario_id=current_user.id).order_by().first()
        if lista:
            publicacoes = lista.publicacoes.order_by(Publicacao.data_gravacao.desc()).limit(filtros['limit']).offset(filtros['skip']).all()

    return jsonify({'erro': '', 'dados': [p.dicionario() for p in publicacoes]})
