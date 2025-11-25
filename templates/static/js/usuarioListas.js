function abrirSobreTelaLista(gravarLivro=false){
    var sobretelaInfoLista = document.getElementById('sobretelaInfoLista');
    var btnSalvarLista = document.getElementById('btnSlavarLista');
    gravarLivro ? btnSalvarLista.classList.add("gravar") : btnSalvarLista.className = "btnPrimario";
    abrirSobreTela('sobretelaInfoLista');
    document.getElementById("idListaLivro").value = "0";
    sobretelaInfoLista.querySelector('.tituloBarra').innerHTML = "Criar Lista";
    document.getElementById("nomeListaLivro").value = "";
    document.getElementById("descricaoListaLivro").value = "";
    document.getElementById("visibilidade").value = "0";
}

async function abrirSobreTelaListaEditar(){
    if (!await usuarioEstaLogado()){
        toast.info("Refaça o seu login para editar");
        return;
    }

    var sobretelaInfoLista = document.getElementById('sobretelaInfoLista');
    abrirSobreTela('sobretelaInfoLista');
    document.getElementById("idListaLivro").value = idListaAtual;
    sobretelaInfoLista.querySelector('.tituloBarra').innerHTML = "Editar Lista";

    fetch('/retornarListaLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idListaAtual})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("nomeListaLivro").value = data.nome;
        document.getElementById("descricaoListaLivro").value = data.descricao;
        document.getElementById("visibilidade").value = data.visibilidade;
    }).catch(error => { console.error('Erro:', error); });
}

function salvarLista(){
    var gravarLivro = event.target.classList.contains("gravar") ? true : false;

    var erroSalvarLista = document.getElementById("erroSalvarLista");
    erroSalvarLista.innerHTML = "";
    var nomeListaLivro = document.getElementById("nomeListaLivro");
    var descricaoListaLivro = document.getElementById("descricaoListaLivro").value.trim();
    if (nomeListaLivro.value.trim() == ""){
        adicinoarEdicaoCampoObrigatorio(nomeListaLivro);
        return;
    }

    idListaLivro = document.getElementById("idListaLivro").value;

    lista = {
        id: idListaLivro,
        nome: nomeListaLivro.value.trim(),
        descricao: descricaoListaLivro,
        visibilidade: document.getElementById("visibilidade").value
    }

    fetch('/controleListaLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(lista)
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != "") {
            erroSalvarLista.innerHTML = retorno.erro;
        } else {
            alterarListaTela(retorno.lista, gravarLivro);
            fecharSobreTela("sobretelaInfoLista", true);
            if (gravarLivro){
                var idLivro = sobretelaSelecionarListaLivro.getAttribute("idlivro");
                var idListaLivroAtual = sobretelaSelecionarListaLivro.getAttribute("idlistaatual");
                salvarLivro(idLivro, retorno.lista.id, idListaLivroAtual);
            }else{
                toast.sucesso(`Lista ${retorno.alterada ? 'alterada' : 'salva'} com sucesso.`);
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

function retornarListas(){
    var idUsuario = document.getElementById('idUsuario').innerText;

    fetch('/retornarListasLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idUsuario: idUsuario})

    }).then(response => 
        response.json()

    ).then(retorno => {
        areaListasUsuario.innerHTML = "";
        controleAreaVerLivrosLista = document.getElementById('controleAreaVerLivrosLista')
        if (retorno.buscar_apenas_livros){
            document.getElementById("controleListasLivros").remove();
            controleAreaVerLivrosLista.className = "col-lg-12";
            var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
            areaVerLivrosLista.innerHTML = "";
            for (var livro of retorno.livros){
                areaVerLivrosLista.innerHTML += conteudoHtmlLivroUsuario(livro);
            }
            if (retorno.livros == 0){
                controleAreaVerLivrosLista.innerHTML = "Nenhum livro encontrado.";
            }
        }else{
            for (var lista of retorno.listas){
                carregarListaTela(lista);
            }
            if (areaListasUsuario.children.length > 0){
                selecionarLista(areaListasUsuario.children[0])
            }else{
                controleAreaVerLivrosLista.innerHTML = "Nenhuma lista encontrada.";
            }
        }

    }).catch(error => {
        console.error('Erro:', error);
    });
}

var idListaAtual = 0;

function carregarListaTela(lista, gravarLivro=false){

    var areaListasUsuario = document.getElementById("areaListasUsuario");

    var idUsuario = document.getElementById('idUsuario')
    idUsuario = idUsuario ? idUsuario.innerText : 0;

    var div = document.createElement('li');
    div.className = "listalivroitem";
    div.setAttribute("idlista", lista.id);
    div.setAttribute("title", lista.descricao);

    div.innerHTML = `
        <button class="btnMaisInfo"></button>
        <div class="tituloLista">${lista.nome}</div>
    `;

    if (areaListasUsuario && (gravarLivro && idUsuario.toString() == lista.usuario_id || !gravarLivro)){
        areaListasUsuario.appendChild(div);
        div.addEventListener('click', function(event){
            selecionarLista(div);
        });
        criarAcaoBtnMaisInfo(div, lista.id, lista.seguindo);
    }

    var sobretelaSelecionarListaLivro = document.getElementById("sobretelaSelecionarListaLivro");
    if (sobretelaSelecionarListaLivro){
        var idLivro = sobretelaSelecionarListaLivro.getAttribute("idlivro");
        var idListaLivroAtual = sobretelaSelecionarListaLivro.getAttribute("idlistaatual");
        if (idLivro){
            sobretelaSelecionarListaLivro.querySelector(".acaoConteudo").innerHTML += `<button idlista="${lista.id}" onclick="salvarLivro('${idLivro}', ${lista.id}, ${idListaLivroAtual})">${lista.nome}</button>`;;
        }
    }
}

function selecionarLista(divLista){

    //alterarInteracaoPerfil("interacaoPerfilLivrosConteudo");

    var controleListasLivros = document.getElementById("controleListasLivros");
    if (!controleListasLivros){
        return;
    }

    var selAntes = controleListasLivros.querySelector('.listalivroitem.selecionado');
    if (divLista == selAntes && divLista.innerHTML == selAntes.innerHTML){
        return;
    }

    if (selAntes) selAntes.classList.remove('selecionado');
    divLista.classList.add('selecionado');
    document.getElementById('areaDescricaoLista').innerHTML = divLista.getAttribute("title");
    document.getElementById('areaTituloLista').innerHTML = divLista.querySelector(".tituloLista").innerText;
    carregarLivrosLista(divLista.getAttribute("idlista"));
}

function alterarListaTela(lista, gravarLivro=false){
    fecharSobreTela('sobretelaGerenciarLista', true);
    if (!document.getElementById("sobretelaSelecionarListaLivro")){
        fecharSobreTela('sobretelaInfoLista', true);
    }

    var l = document.querySelector('.listalivroitem[idlista="'+lista.id+'"]');
    if (l) {
        var selAntes = controleListasLivros.querySelector('.listalivroitem.selecionado');
        if (selAntes == l){
            
        }
        areaTituloLista = document.getElementById("areaTituloLista");
        if (areaTituloLista){
            areaTituloLista.innerHTML = lista.nome;
        }
        areaDescricaoLista = document.getElementById('areaDescricaoLista')
        if (areaDescricaoLista){
            areaDescricaoLista.innerHTML = lista.descricao;
        }

        l.setAttribute("title", lista.descricao);
        l.querySelector('.tituloLista').innerHTML = lista.nome;
    } else {
        carregarListaTela(lista, gravarLivro);
    }

    if (!gravarLivro){
        l = document.querySelector('.listalivroitem[idlista="'+lista.id+'"]');
        if (l){
            selecionarLista(l)
        }
    }
}

function excluirLista(){
    if (!window.confirm("Deseja realmente excluir a lista?")){
        fecharSobreTela('sobretelaGerenciarLista', true);
        return;
    }

    fetch('/apagarListaLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idListaAtual})

    }).then(response => 
        response.json()

    ).then(data => {
        if (data.erro != "") {
            toast.erro(data.erro);
        } else {
            var controleListasLivros = document.getElementById("controleListasLivros");
            var selAtual = controleListasLivros.querySelector('.listalivroitem[idlista="'+idListaAtual+'"]');
            fecharSobreTela('sobretelaGerenciarLista', true);
            var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
            if (areaVerLivrosLista){
                //areaVerLivrosLista.innerHTML = "";
            }
            
            var selAntes = controleListasLivros.querySelector('.listalivroitem.selecionado');
            if (selAntes.getAttribute("idlista") != selAtual.getAttribute("idlista") && selAntes){
                selecionarLista(selAntes);
            } else if (selAtual.previousElementSibling != null){
                selecionarLista(selAtual.previousElementSibling);
            } else if (selAtual.nextElementSibling != null){
                selecionarLista(selAtual.nextElementSibling);
            }

            Array.prototype.forEach.call(document.querySelectorAll('.listalivroitem[idlista="'+idListaAtual+'"]'), function(sel){
                sel.remove()
            })
        }

    }).catch(error => { console.error('Erro:', error); });
}


function carregarLivrosLista(idLista){
    var idUsuario = document.getElementById('idUsuario').innerText;
    var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
    areaVerLivrosLista.innerHTML = "";  

    /*fetch('/retornarLivrosLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idLista, idUsuario: idUsuario})
    })
    .then(response => response.json())
    .then(retorno => {
        for (var livro of retorno.dados){
            areaVerLivrosLista.innerHTML += conteudoHtmlLivroUsuario(livro);
        }
    }).catch(error => { console.error('Erro:', error); });*/

    new Paginacao("#areaVerLivrosLista", {
        url: '/retornarLivrosLista',
        filtros: {
            idLista: idLista, idUsuario: idUsuario
        },
        conteudoHtml: conteudoHtmlLivroUsuario,
        mostrarBarraPesquisa: true,
        elScroolDeteccao: window,
        logica: function(){
            if (this.paginaAtual == 1 && this.dados.length == 0){
                this.toggleMsg("Nenhum livro salvo nesta lista.");
            }
        }
    });
}


var btnAux = null;
function abrirSalvarLivro(idLivro, btn){
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("salvarLivro", idLivro);
}

function abrirMoverLivro(idLivro, idListaAtual, btn){
    btnAux = btn;
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("moverLivro", idLivro, idListaAtual);
}

function abrirDuplicarLivro(idLivro, idListaAtual, btn){
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("duplicarLivro", idLivro);
}

function salvarLivro(idLivro, idListaAlvo, idListaAtual=null){
    fecharSobreTela('sobretelaSelecionarListaLivro', true);

    if (idListaAtual != null && idListaAtual.toString() != "undefined" && idListaAtual.toString().trim() != ""){
        fetch('/moverLivroLista', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idLivro: idLivro, idListaAtual: idListaAtual, idListaMover: idListaAlvo})
        })
        .then(response => response.json())
        .then(data => {
            if (data.erro != ""){
                toast.erro(data.erro);
                return;
            }else{
                toast.sucesso("Livro movido com sucesso!")
            }

            var lvr = btnAux.closest('.livroItem');
            lvr.remove();
            btnAux = null;
        })
        .catch(error => { console.error('Erro:', error); });

    }else{
        fetch('/vincularLivroLista', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idLivro: idLivro, idLista: idListaAlvo})

        })
        .then(response => response.json())
        .then(data => {
            if (data.erro != ""){
                toast.erro(data.erro);
            }else{
                toast.sucesso("Livro salvo com sucesso!");
                var btnAcaoSalvo = document.getElementById("btnAcaoSalvo");
                if (btnAcaoSalvo){
                    btnAcaoSalvo.classList.add("salvo");
                }
            }
        })
        .catch(error => { console.error('Erro:', error); });
    }
}

function removerLivroLista(idRelacao, idLivro, idLista, btn=null){
    var lvr = btn.closest('.livroItem');
    var lst = document.querySelector('.listalivroitem.selecionado .tituloLista').innerText;
    if (!window.confirm(`Deseja realmente remover o livro '${lvr.querySelector('.dataContent').innerText}' da lista '${lst}'?`)){
        return;
    }
    
    fetch('/desvincularLivroLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idRelacao: idRelacao, idLivro, idLista: idLista})
    })
    .then(response => response.json())
    .then(data => {
        if (data.erro != ""){
            toast.erro(data.erro);
        }else{
            lvr.remove();
            toast.sucesso("Livro removido com sucesso!")
        }
    })
    .catch(error => { console.error('Erro:', error); });
}

function seguirLista(){
    var idUsuario = document.getElementById('idUsuario').innerText;

    fetch('/controleSeguirLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idListaAtual, idUsuarioSeguir: idUsuario})
    })
    .then(response => response.json())
    .then(data => {
        if (data.erro != ""){
            toast.erro(data.erro);
        }else{
            if (data.seguindo){
                toast.sucesso("Você será notificado sobre as atualizações da lista.");
            }
            atualizarBtnSeguirLista(data.seguindo);

            var controleListasLivros = document.getElementById("controleListasLivros");
            var selAtual = controleListasLivros.querySelector('.listalivroitem[idlista="'+idListaAtual+'"]');
            criarAcaoBtnMaisInfo(selAtual, data.idLista, data.seguindo);
        }
    })
    .catch(error => { console.error('Erro:', error); });
}

function criarAcaoBtnMaisInfo(obj, idLista, seguindo){
    var btnMaisInfo = obj.querySelector('.btnMaisInfo');
    if (btnMaisInfo){
        btnMaisInfo.addEventListener('click', function(event){
            event.stopPropagation();
            abrirSobreTela('sobretelaGerenciarLista', this);
            idListaAtual = idLista;
            atualizarBtnSeguirLista(seguindo);
        });
    }
}

function atualizarBtnSeguirLista(seguindo){
    var btnSeguirLista = document.getElementById("btnSeguirLista");
    if (btnSeguirLista){
        if (seguindo){
            btnSeguirLista.style.backgroundColor = "lightgreen";
            btnSeguirLista.innerHTML = "Seguindo";
        }else{
            btnSeguirLista.style.backgroundColor = "unset";
            btnSeguirLista.innerHTML = "Seguir";
        }
    }
}

function atualizarSobretelaSelecionarLista(acao, idLivro, idListaLivroAtual){
    fetch('/retornarListasLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})

    }).then(response => 
        response.json()

    ).then(data => {
        var sobretelaSelecionarListaLivro = document.getElementById("sobretelaSelecionarListaLivro");
        sobretelaSelecionarListaLivro.setAttribute("acao", acao);
        sobretelaSelecionarListaLivro.setAttribute("idlivro", idLivro);
        sobretelaSelecionarListaLivro.setAttribute("idlistaatual", idListaLivroAtual);
        var area = sobretelaSelecionarListaLivro.querySelector(".acaoConteudo");
        area.innerHTML = "";
        if (data.erro == ""){
            for (var lista of data.listas){
                if (acao == "salvarLivro" || (acao == "duplicarLivro" && lista.id != idListaLivroAtual)){
                    area.innerHTML += `<button idlista="${lista.id}" onclick="salvarLivro('${idLivro}', ${lista.id})">${lista.nome}</button>`;

                }else if (acao == "moverLivro" && lista.id != idListaLivroAtual){
                    area.innerHTML += `<button idlista="${lista.id}" onclick="salvarLivro('${idLivro}', ${lista.id}, ${idListaLivroAtual})">${lista.nome}</button>`;
                }
            }
        }else{
            area.innerHTML = data.erro + '<a href="login">Ir para tela de login</a>';
        }

    }).catch(error => {
        console.error('Erro:', error);
    });
}