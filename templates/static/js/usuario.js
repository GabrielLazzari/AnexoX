var interacoesPerfil = document.getElementById('interacoesPerfil');
var interacoesPerfilVisualizacao = document.getElementById('interacoesPerfilVisualizacao');
var areaListasUsuario = document.getElementById('areaListasUsuario');

Array.prototype.forEach.call(interacoesPerfil.getElementsByTagName('button'), function(btn){
    btn.addEventListener('click', function(event){
        alterarInteracaoPerfil(btn);
    })
});

function alterarInteracaoPerfil(btn){
    if (!btn){
        return;
    }

    btn_aux = interacoesPerfil.querySelector('.selecionado')
    if (btn_aux.id == btn.id) return;
    btn_aux.classList.remove("selecionado");
    btn.classList.add('selecionado');
    
    interacoesPerfilVisualizacao.querySelector(':scope > .selecionado').classList.remove('selecionado');
    interacoesPerfilVisualizacao.querySelector('#' + btn.id + 'Conteudo').classList.add('selecionado');
    if (btn.id == "interacaoPerfilLivros"){
        retornarListas();

    }else if (btn.id == "interacaoPerfilSeguindo"){
        retornarUsuariosSeguir("seguindo");

    }else if (btn.id == "interacaoPerfilSeguidores"){
        retornarUsuariosSeguir("seguidores");

    }else if (btn.id == "interacaoPerfilPublicacoes"){
        console.log("publicacaoes");
    }
}

var btnSeguirUsuario = document.getElementById('btnSeguirUsuario');
if (btnSeguirUsuario){
    btnSeguirUsuario.addEventListener('click', function(event){
        var idUsuario = document.getElementById('idUsuario').innerText;

        controleSeguirUsuario(idUsuario, btnSeguirUsuario)
    });
}

function controleSeguirUsuario(idUsuarioSeguir, btn){
    fetch('/controleSeguirUsuario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idUsuarioSeguir: idUsuarioSeguir})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != "") {
            toast.erro(retorno.erro);
        }else{
            if (retorno.seguindo){
                btn.innerText = "Seguindo";
            }else{
                btn.innerText = "Seguir";
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

function retornarUsuariosSeguir(tipo="seguindo"){
    if (tipo == "seguindo"){
        tipo = '/retornarUsuariosSeguindo';
    }else{
        tipo = '/retornarUsuariosSeguidores';
    }

    var idUsuario = document.getElementById('idUsuario').innerText;

    fetch(tipo, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idUsuario: idUsuario})
    })
    .then(response => response.json())
    .then(retorno => {
        console.log(retorno);
        if (retorno.erro != "") {
            toast.erro(retorno.erro);
        }else{
            if (tipo == '/retornarUsuariosSeguindo'){
                carregarUsuarioSeguir(retorno.usuarios, document.getElementById('interacaoPerfilSeguindoConteudo'))
            }else{
                carregarUsuarioSeguir(retorno.usuarios, document.getElementById('interacaoPerfilSeguidoresConteudo'))
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

function carregarUsuarioSeguir(usuarios, el){
    el.innerHTML = "";
    for (var usuario of usuarios){
        el.innerHTML += conteudoHtmlUsuario(usuario);
    }
}

retornarListas();

var objPag = null;

function abrirEscolherLivro(){
    abrirSobreTela('sobretelaEscolherLivro');
    if (objPag == null) {
        objPag = new Paginacao("#areaEscolherLivro", {
            url: '/pesquisaLivros',
            conteudoHtml: conteudoHtmlLivroPesquisa,
            mostrarBarraPesquisa: true,
            clickItem: function (itemHtml) {
                var idLista = document.querySelector(".listalivroitem.selecionado").getAttribute("idlista");
                var idLivro = itemHtml.getAttribute("idlivro");
                salvarLivro(idLivro, idLista);
                fecharSobreTela('sobretelaEscolherLivro', true);
                setTimeout(() => {
                    carregarLivrosLista(idLista);
                }, 100);
            }
        });
    }
}

function abrirInfoComentario(btn){
    var comentario = btn.closest(".comentario");
    var idComentario = comentario.querySelector("[idcomentario]").getAttribute("idcomentario");
    idComentarioAux = idComentario;
    abrirSobreTela('sobretelaInfoComentario', btn);
}

var interacaoUsuario = document.getElementById("interacaoUsuario");
if (interacaoUsuario){
    interacaoUsuario = interacaoUsuario.innerText;
    if (interacaoUsuario != "PerfilLivros"){
        var btn = document.getElementById("interacao" + interacaoUsuario);
        alterarInteracaoPerfil(btn);
    }
}

async function recomendarLivro(){
    const response = await fetch("/gerarRecomendacaoLivro", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });

    var resposta = await response.json();

    toast.sucesso("Abra as notificações para ver o livro recomendado");
}