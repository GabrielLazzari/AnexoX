var idPublicacaoAux = 0;
var idListaPublicacaoAux = 0;

function abrirInfoPublicacao(btn){
    var publicacao = btn.closest(".publicacaoItem");
    var idPublicacao = publicacao.querySelector("[idpublicacao]").getAttribute("idpublicacao");
    idPublicacaoAux = idPublicacao;
    abrirSobreTela('sobretelaInfoPublicacao', btn);

    var btnExcluirPublicacaoDaLista = document.getElementById("btnExcluirPublicacaoDaLista");
    btnExcluirPublicacaoDaLista.style.display = "none";

    if (window.location.pathname == "/usuario"){
        var item = document.querySelector(".listapublicacaoitem.selecionado");
        if (item && item.id == "btnMinhasPublicacoes"){
            btnExcluirPublicacaoDaLista.style.display = "none";
        }else{
            btnExcluirPublicacaoDaLista.style.display = "block";
        }
    }
}

function reagirPublicacao(btn){
    btn.classList.toggle("reagido");

    var publicacao = btn.closest(".publicacaoItem");
    var idPublicacao = publicacao.querySelector("[idpublicacao]").getAttribute("idpublicacao");

    fetch('/reagirPublicacao', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            idPublicacao: idPublicacao,
            reagido: btn.classList.contains("reagido")
        })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }
    }).catch(error => { console.error('Erro:', error); });
}

function compartilharPublicacao(idPublicacao){
    var publicacao = event.target.closest(".publicacaoItem");
    var titulo = "Publicação de " + publicacao.querySelector(".publicacaoNomeUsuario").innerText;
    var texto = publicacao.querySelector(".publicacaoConteudo").innerText.trim();

    if (texto != ""){
        if (texto.length > 50) {
            texto = texto.substring(0, 50);
        }
    }else{
        texto = titulo;
    }

    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: texto,
            url: window.location.origin + "/publicacao?id=" + idPublicacao
        });
    } else {
        navigator.clipboard.writeText(window.location.origin + "/publicacao?id=" + idPublicacao).then(() => {
            toast.sucesso('Link copiado para a área de transferência!');
        });
    }
}

function abrirSalvarPublicacao(idPublicacao=''){
    abrirSobreTela("sobretelaSalvarPublicacao");
    document.getElementById("tituloSalvarListaPublicacao").innerHTML = "Salvar Publicação";
    retornarListasPublicacao(true);

    var sobretelaSalvarPublicacao = document.getElementById("sobretelaSalvarPublicacao");
    sobretelaSalvarPublicacao.querySelector("[idpublicacao]").setAttribute("idpublicacao", idPublicacao);
}

async function abrirSobreTelaListaPublicacoesEditar(){
    abrirSobreTela("sobretelaSalvarPublicacao");
    document.getElementById("tituloSalvarListaPublicacao").innerHTML = "Editar Publicação";
    lista = await retornarListaPublicacao(idListaPublicacaoAux);
    document.getElementById("nomeListaPublicacao").value = lista.nome;
    document.getElementById("descricaoListaPublicacao").value = lista.descricao;
}

function salvarListaPublicacao(){
    var sobretelaSalvarPublicacao = document.getElementById("sobretelaSalvarPublicacao");
    
    var idPublicacao = sobretelaSalvarPublicacao.querySelector("[idpublicacao]").getAttribute("idpublicacao");
    var idLista = salvarPublicacaoListasSalvar.querySelector(".listaPublicacaoEscolha.selecionado");
    console.log(idPublicacao, idLista)
    if (idLista){
        idLista = idLista.getAttribute("idlistapublicacao");
        salvarPublicacao(idPublicacao, idLista);

    }else{
        var nomeLista = document.getElementById("nomeListaPublicacao").value;
        var descricao = document.getElementById("descricaoListaPublicacao").value;

        idLista = idListaPublicacaoAux;

        fetch('/controleListaPublicacao', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                idLista: idLista,
                nomeLista: nomeLista,
                descricao: descricao
            })
        })
        .then(response => response.json())
        .then(retorno => {
            console.log(retorno)
            if (retorno.erro != ""){
                toast.erro(retorno.erro);
            }else{
                if (idPublicacao && idPublicacao != ""){
                    salvarPublicacao(idPublicacao, retorno.listaPublicacao.id);
                    carregarListaPublicacao(retorno.listaPublicacao, false);
                }else{
                    toast.sucesso("Lista atualizada com sucesso!");
                    fecharSobreTela('sobretelaSalvarPublicacao', true);
                    fecharSobreTela('sobretelaGerenciarListaPublicacoes', true);
                    Array.prototype.forEach.call(document.querySelectorAll('.listapublicacaoitem[idlistapublicacao="'+idListaPublicacaoAux+'"]'), function(sel){
                        sel.querySelector(".tituloLista").innerText = retorno.listaPublicacao.nome;
                    })
                }
            }
        }).catch(error => { console.error('Erro:', error); });   
    }
}

function salvarPublicacao(idPublicacao, idListaPublicacao){
    fetch('/salvarPublicacaoLista', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            idPublicacao: idPublicacao,
            idListaPublicacao: idListaPublicacao
        })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            toast.sucesso("Publicação salva com sucesso!");
            fecharSobreTela('sobretelaSalvarPublicacao', true);
        }
    }).catch(error => { console.error('Erro:', error); });
}

function excluirPublicacao(){
    if (idPublicacaoAux == 0){
        toast.erro("Selecione uma publicação escrita por você para excluir");
        return;
    }

    if (!window.confirm(`Deseja realmente remover a publicação?`)){
        return;
    }

    fecharSobreTela('sobretelaInfoPublicacao', true);

    fetch('/excluirPublicacao', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idPublicacao: idPublicacaoAux})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            document.querySelector("[idpublicacao='" + idPublicacaoAux + "']").closest(".publicacaoItem").remove();
            toast.sucesso("Publicacao removida com sucesso!");
        }
    }).catch(error => { console.error('Erro:', error); });
}

function excluirPublicacaoDaLista(){
    var idLista = document.querySelector(".listapublicacaoitem.selecionado");
    if (idLista){
        idLista = idLista.getAttribute("idlistapublicacao");
        fetch('/excluirPublicacaoDaLista', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idListaPublicacao: idLista, idPublicacao: idPublicacaoAux})
        })
        .then(response => response.json())
        .then(retorno => {
            if (retorno.erro != ""){
                toast.erro(retorno.erro);
            }else{
                var areaVerPublicacoesLista = document.querySelector("#areaVerPublicacoesLista");
                if (areaVerPublicacoesLista){
                    document.querySelector("[idpublicacao='" + idPublicacaoAux + "']").closest(".publicacaoItem").remove();
                    fecharSobreTela("sobretelaInfoPublicacao", true);
                    toast.sucesso("Publicacao removida com sucesso da lista!");
                }
            }
        }).catch(error => { console.error('Erro:', error); });

    }else{
        toast.erro("Selecione uma lista para excluir a publicação");
    }
}

function excluirListaPublicacao(){
    if (!window.confirm("Deseja realmente excluir a lista?")){
        fecharSobreTela('sobretelaGerenciarLista', true);
        return;
    }

    fetch('/excluirListaPublicacao', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idListaPublicacao: idListaPublicacaoAux})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            var controlePublicacoes = document.getElementById("controlePublicacoes");
            var selAtual = controlePublicacoes.querySelector('.listapublicacaoitem[idlistapublicacao="'+idListaPublicacaoAux+'"]');
            fecharSobreTela('sobretelaGerenciarListaPublicacoes', true);
            
            var selAntes = controlePublicacoes.querySelector('.listapublicacaoitem.selecionado');

            if (selAntes.getAttribute("idlistapublicacao") != selAtual.getAttribute("idlistapublicacao") && selAntes){
                selecionarListaPubliacao(selAntes);
            } else if (selAtual.previousElementSibling != null){
                selecionarListaPubliacao(selAtual.previousElementSibling);
            } else if (selAtual.nextElementSibling != null){
                selecionarListaPubliacao(selAtual.nextElementSibling);
            }

            Array.prototype.forEach.call(document.querySelectorAll('.listapublicacaoitem[idlistapublicacao="'+idListaPublicacaoAux+'"]'), function(sel){
                sel.remove()
            })
        }
    }).catch(error => { console.error('Erro:', error); });
}

var areaListasPublicacoes = document.getElementById("areaListasPublicacoes");
function retornarListasPublicacao(carregarEscolha){
    fetch('/retornarListasPublicacao', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            if (carregarEscolha){
                var salvarPublicacaoListasSalvar = document.getElementById("salvarPublicacaoListasSalvar");
                if (salvarPublicacaoListasSalvar){
                    salvarPublicacaoListasSalvar.innerHTML = "";
                }

            }else if (areaListasPublicacoes){
                areaListasPublicacoes.innerHTML = "";
            }

            for (var lista of retorno.listas){
                carregarListaPublicacao(lista, carregarEscolha);
            }

            var controlePublicacoes = document.getElementById("controlePublicacoes");
            if (controlePublicacoes){
                elSel = controlePublicacoes.querySelector('.listapublicacaoitem.selecionado');
                console.log("elsel", elSel)
                if (!elSel){
                    elSel = controlePublicacoes.querySelector('.listapublicacaoitem');
                    if (elSel){
                        selecionarListaPubliacao(elSel);
                    }
                }
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

async function retornarListaPublicacao(idListaPublicacao){
    const response = await fetch("/retornarListaPublicacao", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idListaPublicacao: idListaPublicacao })
    });

    var resposta = await response.json()
    return resposta;
}

function carregarListaPublicacao(lista, carregarEscolha){
    var divItem = document.createElement("div");
    divItem.setAttribute('idlistapublicacao', lista.id);
    divItem.innerHTML = lista.nome;

    if (carregarEscolha){
        var salvarPublicacaoListasSalvar = document.getElementById("salvarPublicacaoListasSalvar");
        if (salvarPublicacaoListasSalvar){
            divItem.className = "listaPublicacaoEscolha";
            divItem.addEventListener('click', function(){
                Array.prototype.forEach.call(salvarPublicacaoListasSalvar.querySelectorAll(".listaPublicacaoEscolha"), function(item){
                    if (item != divItem){
                        item.classList.remove("selecionado");
                    }
                });

                divItem.classList.toggle("selecionado");

                var salvarPublicacaoListasNova = document.getElementById("salvarPublicacaoListasNova");
                console.log(divItem.classList.contains("selecionado"))
                if (divItem.classList.contains("selecionado")){
                    salvarPublicacaoListasNova.classList.add("desativado");
                }else{
                    salvarPublicacaoListasNova.classList.remove("desativado");
                }
            })
            salvarPublicacaoListasSalvar.insertAdjacentElement('beforeend', divItem);
        }

    } else if (areaListasPublicacoes){
        divItem.className = "listapublicacaoitem";

        divItem.innerHTML = `
            <button class="btnMaisInfo"></button>
            <div class="tituloLista">${lista.nome}</div>
        `;

        divItem.addEventListener('click', function(){
            selecionarListaPubliacao(divItem);
        });

        var btnMaisInfo = divItem.querySelector('.btnMaisInfo');
        if (btnMaisInfo){
            btnMaisInfo.addEventListener('click', function(event){
                event.stopPropagation();
                abrirSobreTela('sobretelaGerenciarListaPublicacoes', this);
                idListaPublicacaoAux = lista.id;
            });
        }

        areaListasPublicacoes.insertAdjacentElement('beforeend', divItem);
    }
}

function selecionarListaPubliacao(divLista){
    var selAntes = document.getElementById("controlePublicacoes").querySelector('.listapublicacaoitem.selecionado');
    if (divLista == selAntes && divLista.innerHTML == selAntes.innerHTML){
        return;
    }

    if (selAntes) selAntes.classList.remove('selecionado');
    divLista.classList.add('selecionado');
    carregarPublicacaoesUsuario(divLista.getAttribute("idlistapublicacao"));
}

function carregarPublicacaoesUsuario(idListaPublicacao){
    new Paginacao("#areaVerPublicacoesLista", {
        url: '/retornarPublicacoesLista',
        filtros: {
            'idListaPublicacao': idListaPublicacao,
            'idUsuario': document.getElementById('idUsuario').innerText
        },
        conteudoHtml: conteudoHtmlPublicacao,
        flex: false,
        elScroolDeteccao: document.getElementById("conteudo"),
        qtdElPorPagina: 5,
        logica: function(){
            if (this.paginaAtual == 1 && this.dados.length == 0){
                this.toggleMsg("Nenhum comentário encontrado para o livro. Seje o primeiro(a) a comentar.");
            }
        }
    });
}

var controlePublicacoes = document.getElementById("controlePublicacoes");
if (controlePublicacoes){
    retornarListasPublicacao(false);
}else if (document.getElementById('idUsuario')){
    carregarPublicacaoesUsuario("minhaspublicacoes")
}
