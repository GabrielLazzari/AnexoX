var interacoesPerfil = document.getElementById('interacoesPerfil2');
var interacoesPerfilVisualizacao = document.getElementById('interacoesPerfilVisualizacao');
var areaListasUsuario = document.getElementById('areaListasUsuario');

var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
var areaVerPublicacoesLista = document.getElementById('areaVerPublicacoesLista');
var interacaoPerfilSeguindoConteudo = document.getElementById('interacaoPerfilSeguindoConteudo');
var interacaoPerfilSeguidoresConteudo = document.getElementById('interacaoPerfilSeguidoresConteudo');

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

    areaVerLivrosLista.innerHTML = "";
    areaVerPublicacoesLista.innerHTML = "";
    interacaoPerfilSeguindoConteudo.innerHTML = "";
    interacaoPerfilSeguidoresConteudo.innerHTML = "";

    if (btn.id == "interacaoPerfilLivros"){
        retornarListas();

    }else if (btn.id == "interacaoPerfilSeguindo"){
        retornarUsuariosSeguir("seguindo");

    }else if (btn.id == "interacaoPerfilSeguidores"){
        retornarUsuariosSeguir("seguidores");

    }else if (btn.id == "interacaoPerfilPublicacoes"){
        var btnMinhasPublicacoes = document.getElementById("btnMinhasPublicacoes");
        if (btnMinhasPublicacoes){
            selecionarListaPubliacao(document.getElementById("btnMinhasPublicacoes"));
        }else{
            carregarPublicacaoesUsuario('minhaspublicacoes')
        }
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
        body: JSON.stringify({idUsuario: idUsuario, tipoSeguindo: 'seguindo'})
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

    /*var elemento = tipo == "seguindo" ? "interacaoPerfilSeguindoConteudo" : "interacaoPerfilSeguidoresConteudo";
    var tipoSeguindo = tipo == "seguindo" ? "seguindo" : "seguidor";

    var idUsuario = document.getElementById('idUsuario').innerText;

    new Paginacao("#" + elemento, {
        url: '/retornarUsuariosSeguir',
        filtros: {
            idUsuario: idUsuario, tipoSeguindo: tipoSeguindo
        },
        conteudoHtml: conteudoHtmlUsuario,
        mostrarBarraPesquisa: true,
        elScroolDeteccao: window
    });*/
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

/*function abrirInfoComentario(btn){
    var comentario = btn.closest(".comentario");
    var idComentario = comentario.querySelector("[idcomentario]").getAttribute("idcomentario");
    idComentarioAux = idComentario;
    var sobretelaInfoComentario = document.getElementById("sobretelaInfoComentario");

    if (sobretelaInfoComentario){
        var btnExcluirComentario = sobretelaInfoComentario.querySelector("#btnExcluirComentario");
        console.log('pppppp', window.location.pathname)
        if (window.location.pathname == "/livro"){
            btnExcluirComentario.setAttribute("onclick", "excluirComentario('livro')");
        }else{
            btnExcluirComentario.setAttribute("onclick", "excluirComentario('publicacao')");
        }
    }

    abrirSobreTela('sobretelaInfoComentario', btn);
}*/

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

    if (resposta.tem_notificacao){
        toast.sucesso("Abra as notificações para ver o livro recomendado");
        atualizarNotificacoes();
    }else{
        toast.info("Nenhum livro recomendado no momento. Continue interagindo para receber recomendações!");
    }
}
