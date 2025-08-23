function abrirSobreTelaLista(){
    var sobretelaInfoLista = document.getElementById('sobretelaInfoLista');
    abrirSobreTela('sobretelaInfoLista');
    document.getElementById("idListaLivro").value = "0";
    sobretelaInfoLista.querySelector('.tituloBarra').innerHTML = "Criar Lista";
    document.getElementById("nomeListaLivro").value = "";
    document.getElementById("descricaoListaLivro").value = "";
    document.getElementById("visibilidade").value = "0";
}

function abrirSobreTelaListaEditar(){
    var sobretelaInfoLista = document.getElementById('sobretelaInfoLista');
    abrirSobreTela('sobretelaInfoLista');
    document.getElementById("idListaLivro").value = idListaAtual;
    sobretelaInfoLista.querySelector('.tituloBarra').innerHTML = "Editar Lista";
    
    var idUsuario = document.getElementById('idUsuario').innerText;

    fetch('/retornarListaLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idListaAtual, idUsuario: idUsuario})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("nomeListaLivro").value = data.nome;
        document.getElementById("descricaoListaLivro").value = data.descricao;
        document.getElementById("visibilidade").value = data.visibilidade;
    }).catch(error => { console.error('Erro:', error); });
}

function salvarLista(){
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
        console.log('r', retorno)
        if (retorno.erro != "") {
            erroSalvarLista.innerHTML = retorno.erro;
        } else {
            alterarListaTela(retorno.lista);
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

    ).then(data => {
        areaListasUsuario.innerHTML = "";
        for (var lista of data.listas){
            carregarListaTela(lista);
        }
        if (areaListasUsuario.children.length > 0){
            selecionarLista(areaListasUsuario.children[0])
        }

    }).catch(error => {
        console.error('Erro:', error);
    });
}

var idListaAtual = 0;

function carregarListaTela(lista){
    if (!areaListasUsuario ){
        return;
    }

    var idUsuario = document.getElementById('idUsuario').innerText;

    var div = document.createElement('div');
    div.className = "listalivroitem";
    div.setAttribute("idlista", lista.id);
    div.setAttribute("title", lista.descricao);

    console.log(lista.usuario_id, idUsuario)

    div.innerHTML = `
        ${lista.usuario_id == idUsuario ? '<button class="btnMaisInfo"></button>' : ''}
        <div class="tituloLista">${lista.nome}</div>
    `;

    areaListasUsuario.appendChild(div);
    div.addEventListener('click', function(event){
        selecionarLista(div);
    });
    var btnMaisInfo = div.querySelector('.btnMaisInfo');
    if (btnMaisInfo){
        btnMaisInfo.addEventListener('click', function(event){
            abrirSobreTela('sobretelaGerenciarLista', this);
            idListaAtual = lista.id;
        });
    }
}

function selecionarLista(divLista){
    var selAntes = document.querySelector('.listalivroitem.selecionado');
    if (selAntes) selAntes.classList.remove('selecionado');
    divLista.classList.add('selecionado');
    document.getElementById('areaDescricaoLista').innerHTML = divLista.getAttribute("title");
    carregarLivrosLista(divLista.getAttribute("idlista"));
}

function alterarListaTela(lista){
    fecharSobreTela('sobretelaGerenciarLista', true);
    fecharSobreTela('sobretelaInfoLista', true);
    console.log(lista);
    var l = document.querySelector('.listalivroitem[idlista="'+lista.id+'"]');
    if (l) {
        l.querySelector('.tituloLista').innerHTML = lista.nome;
    } else {
        carregarListaTela(lista);
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
            document.querySelector('.listalivroitem[idlista="'+idListaAtual+'"]').remove();
            fecharSobreTela('sobretelaGerenciarLista', true);
            var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
            if (areaVerLivrosLista){
                areaVerLivrosLista.innerHTML = "";
            }            
        }

    }).catch(error => { console.error('Erro:', error); });
}


function carregarLivrosLista(idLista){
    var idUsuario = document.getElementById('idUsuario').innerText;
    var areaVerLivrosLista = document.getElementById('areaVerLivrosLista');
    areaVerLivrosLista.innerHTML = "";  

    fetch('/retornarLivrosLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLista: idLista, idUsuario: idUsuario})
    })
    .then(response => response.json())
    .then(retorno => {
        for (var livro of retorno.livros){
            areaVerLivrosLista.innerHTML += conteudoHtmlLivroUsuario(livro);
        }
    }).catch(error => { console.error('Erro:', error); });
}


var btnAux = null;
function abrirSalvarLivro(idLivro, btn){
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("salvarLivro", idLivro, '');
}

function abrirMoverLivro(idLivro, idListaAtual, btn){
    btnAux = btn;
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("moverLivro", idLivro, idListaAtual);
}

function abrirDuplicarLivro(idLivro, idListaAtual, btn){
    abrirSobreTela('sobretelaSelecionarListaLivro', btn);
    atualizarSobretelaSelecionarLista("duplicarLivro", idLivro, idListaAtual);
}

function salvarLivro(idLivro, idLista){
    console.log(idLivro, idLista)
    fecharSobreTela('sobretelaSelecionarListaLivro', true);
    fetch('/vincularLivroLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLivro: idLivro, idLista: idLista})

    })
    .then(response => response.json())
    .then(data => {
        if (data.erro != ""){
            toast.erro(data.erro);
        }
    })
    .catch(error => { console.error('Erro:', error); });
}

function moverLivro(idLivro, idListaAtual, idListaMover){
    fecharSobreTela('sobretelaSelecionarListaLivro', true);
    fetch('/moverLivroLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idLivro: idLivro, idListaAtual: idListaAtual, idListaMover: idListaMover})
    })
    .then(response => response.json())
    .then(data => {
        if (data.erro != ""){
            toast.erro(data.erro);
            return;
        }
        console.log('bt', btnAux)
        var lvr = btnAux.closest('.livroItem');
        lvr.remove();
        btnAux = null;
    })
    .catch(error => { console.error('Erro:', error); });
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
        }
    })
    .catch(error => { console.error('Erro:', error); });
}

function atualizarSobretelaSelecionarLista(acao, idLivro, idListaLivroAtual){
    fetch('/retornarListasLivro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})

    }).then(response => 
        response.json()

    ).then(data => {
        var area = document.getElementById("sobretelaSelecionarListaLivro").querySelector(".acaoConteudo");
        area.innerHTML = "";
        console.log('d', data)
        if (data.erro == ""){
            for (var lista of data.listas){
                if (acao == "salvarLivro" || (acao == "duplicarLivro" && lista.id != idListaLivroAtual)){
                    area.innerHTML += `<button onclick="salvarLivro(${idLivro}, ${lista.id})">${lista.nome}</button>`;

                }else if (acao == "moverLivro" && lista.id != idListaLivroAtual){
                    area.innerHTML += `<button onclick="moverLivro(${idLivro}, ${idListaLivroAtual}, ${lista.id})">${lista.nome}</button>`;
                }
            }
        }else{
            area.innerHTML = data.erro + '<a href="login">Ir para tela de login</a>';
        }

    }).catch(error => {
        console.error('Erro:', error);
    });
}