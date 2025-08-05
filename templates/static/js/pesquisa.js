conteudo = document.getElementById("conteudo");
barraPesquisa = document.getElementById("barraPesquisa");
var btnsAlterarFiltros = document.getElementById("btnsAlterarFiltros");
var areaPesquisa = document.getElementById("areaPesquisa");


function executarPesquisa(pesquisa){
    if (pesquisa){
        campoPesquisa.value = pesquisa;
    }

    fecharSobreTela(caixaPesquisa, obrigarFechamento=true);

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = "pesquisa";

    for (const [chave, valor] of Object.entries(retornarFiltrosPesquisa())) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = chave;
        input.value = valor;
        form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
}

function obterSugestaoNomes(valor){
    fetch('/sugestaoPesquisa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'valor': valor})

    }).then(response => 
        response.json()

    ).then(data => {
        atualizarCaixaPesquisa(data)

    }).catch(error => {
        console.error('Erro:', error);
    });
}

function atualizarCaixaPesquisa(valores){
    if (!valores){
        valores = {pesquisa: [], livros: [], usuarios: []}
    }
    
    resultadoPesquisa.innerHTML = "";
    for (var valor of valores.pesquisa){
        resultadoPesquisa.innerHTML += `
            <button class="previewPesquisaResultado" onclick="executarPesquisa('${valor}')">${valor}</button>
        `;
    }

    resultadoLivros.innerHTML = "";
    resultadoLivros.previousElementSibling.style.display = valores.livros.length == 0 ? "none" : "flex";
    resultadoLivros.style.display = valores.livros.length == 0 ? "none" : "flex";
    for (var livro of valores.livros){
        resultadoLivros.innerHTML += `
            <a href="livro?id=${livro.id}" class="previewPesquisaLivro">
                <img src="${livro.img}" alt="" class="previewPesquisaImgLivro">
                <div>
                    <div class="previewPesquisaTituloLivro">${livro.titulo}</div>
                    <br>
                    <div class="previewPesquisaAutorLivro">${livro.autor}</div>
                </div>
            </a>
        `;
    }

    resultadoUsuario.innerHTML = "";
    resultadoUsuario.previousElementSibling.style.display = valores.usuarios.length == 0 ? "none" : "flex";
    resultadoUsuario.style.display = valores.usuarios.length == 0 ? "none" : "flex";
    for (var usuario of valores.usuarios){
        resultadoUsuario.innerHTML += `
            <a href="usuario?id=${usuario.id}" class="previewPesquisaUsuario">
                <img src="${usuario.img}" alt="" class="previewPesquisaImgUsuario">
                <div class="previewPesquisaNomeUsuario">${usuario.nome}</div>
            </a>
        `;
    }

    atualizarMovimentacaoTeclado("caixaPesquisa");
    atualizarTamanhoCaixaPesquisa();
}

function trocarTipoFiltro(nomeFiltro){
    if (nomeFiltro != null){
        if (nomeFiltro=="livros"){ valoresFiltro.checkLivros = true; }
        else if (nomeFiltro=="leitores"){ valoresFiltro.checkLeitores = true; }
        else if (nomeFiltro=="autores"){ valoresFiltro.checkAutores = true; }
        else if (nomeFiltro=="editoras"){ valoresFiltro.checkEditoras = true; }
        else if (nomeFiltro=="publicacoes"){ valoresFiltro.checkPublicacoes = true; }

        // realizar pesquisa
    }else{
        if (valoresFiltro.checkLivros) { nomeFiltro="livros"; }
        else if (valoresFiltro.checkLeitores) { nomeFiltro="leitores"; }
        else if (valoresFiltro.checkAutores) { nomeFiltro="autores"; }
        else if (valoresFiltro.checkEditoras) { nomeFiltro="editoras"; }
        else if (valoresFiltro.checkPublicacoes) { nomeFiltro="publicacoes"; }
        else { nomeFiltro="livros"; }

        var btn = document.getElementById("btnFiltroRapido" + nomeFiltro[0].toUpperCase() + nomeFiltro.slice(1));
        if (btn != null){
            btn.style.backgroundColor = "var(--corDestaque)";
            btn.querySelector("hr").style.borderColor = "var(--corPrimaria)";
        }
    }
}
trocarTipoFiltro();

function atualizarTamanhoBtnsAlterarFiltros(){
    if (barraPesquisa == null || btnsAlterarFiltros == null){
        return;
    }

    if (window.innerWidth < 450){
        btnsAlterarFiltros.style.left = "5px";
    }else{
        btnsAlterarFiltros.style.left = barraPesquisa.getBoundingClientRect().left - 5 + "px"
    }

    btnsAlterarFiltros.style.top = 7 + "px";
}

window.addEventListener('resize', event => {
    atualizarTamanhoBtnsAlterarFiltros();
});

if (areaPesquisa != null && btnsAlterarFiltros != null){
    areaPesquisa.style.top = btnsAlterarFiltros.getBoundingClientRect().top + "px";
}

atualizarTamanhoBtnsAlterarFiltros();
