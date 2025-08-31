function conteudoHtmlLivro(livro){
    return `
        <div class="livroItem">
            <div class="areaCabecalho">
                <img class="imgLivro" src="${livro.img}">
                <div class="controles">
                    <button class="btnAnimaRotate" onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-m"></button>
                    <button class="btnAnimaRotate" onclick="abrirSalvarLivro('${livro.id}', this)" title="Salvar na Lista"><img src="static/icones/bookmark-outline.svg" alt="" class="svg-m"></button>
                </div>
            </div>
            <div>
                <div class="dataLabel">Título</div>
                <div class="dataContent"><a href="livro?id=${livro.id}">${livro.titulo}</a></div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Autor</div>
                <div class="dataContent"><a href="usuario?id=${livro.idAutor}">${livro.autor}</a></div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Editora</div>
                <div class="dataContent"><a href="usuario?id=${livro.idEditora}">${livro.editora}</a></div>
            </div>
        </div>
    `;
}

function conteudoHtmlLivroUsuario(livro){
    var idUsuario = document.getElementById('idUsuario')?.innerText;

    var controles = ``;
    console.log('id', idUsuario, livro.usuario_id)

    if (idUsuario == livro.usuario_id){
        controles = `
            <div class="controles">
                <button class="btnAnimaRotate" onclick="removerLivroLista('${livro.idRelacao}', '${livro.id}', '${livro.idLista}', this)" title="Remover da Lista"><img src="static/icones/trash-outline.svg" alt="" class="svg-mm"></button>
                <button class="btnAnimaRotate" onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-mm"></button>
                <button class="btnAnimaRotate" onclick="abrirMoverLivro('${livro.id}', '${livro.idLista}', this)" title="Mover para Lista"><img src="static/icones/swap-horizontal-outline.svg" alt="" class="svg-mm"></button>
                <button class="btnAnimaRotate" onclick="abrirDuplicarLivro('${livro.id}', '${livro.idLista}', this)" title="Duplicar para Lista"><img src="static/icones/duplicate-outline.svg" alt="" class="svg-mm"></button>
            </div>
        `;
    }else{
        controles = `
            <div class="controles">
                <button class="btnAnimaRotate" onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-m"></button>
                <button class="btnAnimaRotate" onclick="abrirSalvarLivro('${livro.id}', this)" title="Salvar na Lista"><img src="static/icones/bookmark-outline.svg" alt="" class="svg-m"></button>
            </div>
        `;
    }

    return `
        <div class="livroItem" href="livro?id=${livro.id}">
            <div class="areaCabecalho">
                <img class="imgLivro" src="${livro.img}">
                ${controles}
            </div>
            <div>
                <div class="dataLabel">Título</div>
                <div class="dataContent"><a href="livro?id=${livro.id}">${livro.titulo}</a></div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Autor</div>
                <div class="dataContent"><a href="usuario?id=${livro.idAutor}">${livro.autor}</a></div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Editora</div>
                <div class="dataContent"><a href="usuario?id=${livro.idEditora}">${livro.editora}</a></div>
            </div>
        </div>
    `;
}

function conteudoHtmlUsuario(usuario){
    var href = `href="usuario?id=${usuario.id}"`
    var tag = "a";
    if (usuario.id == 0){
        href = ""
        tag = "div"
    }
    return `
        <${tag} class="usuarioItem" ${href}>
            <img class="imgLivro" src="${usuario.img}">
            <div>${usuario.nome}</div>
        <${tag}>
    `;
}

function conteudoHtmlPublicacao(publicacao){
    return `
        <div class="publicacaoItem">
            <div class="publicacaoItemCabecalho">
                <img src="${publicacao.imgUsuario}">
                <div>
                    <div>${publicacao.nomeUsuario}</div>
                    <div class="datahora">${publicacao.data} as ${publicacao.hora}</div>
                </div>
                <button class="btnMaisInfo"></button>
            </div>
            <div class="publicacaoItemConteudo">
                <div class="publicacaoTitulo">${publicacao.titulo}</div>
                <div class="publicacaoTexto">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Veniam perspiciatis quis tempore distinctio soluta cum obcaecati.</div>
                <div class="publicacaoObjetos">
                    <img src="static/imagens/livros/OsCriadoresDeCoincidencias.jpeg">
                </div>
                <div class="publicacaoAcoes">
                    <button class="btnReagir" onclick="this.classList.toggle('reagido');"></button>
                    <button class="btnReagir" onclick="this.classList.toggle('reagido');"></button>
                    <button><img src="static/icones/arrow-redo-outline.svg"></button>
                </div>
            </div>
            <div class="publicacaoItemComentario">
                <hr>
                ${conteudoHtmlComentario(publicacao)}

                ${conteudoHtmlComentario(publicacao, true)}
            </div>
        <div>
    `;
}

function conteudoHtmlComentario(comentario, tab=false){
    return `
        <div class="comentario ${tab ? 'comentarioTab' : ''}">
            <img src="${comentario.imgUsuario}">
            <div>
                <div class="comentarioCabecalho">
                    <div>${comentario.nomeUsuario}</div>
                    <button class="btnMaisInfo"></button>
                </div>
                <div class="comentarioConteudo">
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Veniam perspiciatis quis tempore distinctio soluta cum obcaecati, fugit alias aliquam suscipit. Quisquam veniam aperiam ea ex qui error quos sit quae.
                </div>
                <div class="comentarioAcoes">
                    <button class="btnComentar">Comentar</button>
                    <button class="btnReagir" onclick="this.classList.toggle('reagido');"></button>
                </div>
            </div>
        </div>
    `
}

class Paginacao{
    constructor(el, filtros, qtdTotalElementos=0, qtdElPorPagina=20){
        // configuracoes basicas
        this.el = el;
        this.filtros = filtros;
        this.conteudoHtml = '';
        this.paginaAtual = filtros['paginaAtual'] ?? 1;
        this.qtdTotalElementos = qtdTotalElementos;
        this.qtdElPorPagina = qtdElPorPagina;

        // configuracoes de personalizacao
        this.limparAoCarregar = true;

        // configuracoes internas
        this.criarEstrutura();

        this.distanciaCarregar = 100;
        this.scrollFim = false;
        this.scrollComeco = false;
        this.atualScrollTop = 0;
        this.ultimoScroolTop = 0;
        this.tempoEspera = 0;

        this.qtdPaginas = Math.ceil(this.qtdTotalElementos / this.qtdElPorPagina);

        console.log('construir')
        this.atualizarHtmlBaixo();

        this.elPaginacaoItens.addEventListener('scroll', (e) => {
            this.controleScrool();
        });

        this.atualizarTamanho();
        window.addEventListener("resize", this.atualizarTamanho.bind(this));
    }

    criarEstrutura(){
        this.el.innerHTML = "";
        this.el.classList.add("paginacao");
        this.el.insertAdjacentHTML("beforeend", '<div class="paginacaoItens"></div>');
        this.el.insertAdjacentHTML("beforeend", '<div class="paginacaoControle"><div class="paginacaoControleNumeracao"></div><div class="paginacaoControleBotoes"></div></div>');
        this.elPaginacaoItens = this.el.querySelector(".paginacaoItens");
        this.paginacaoControle = this.el.querySelector(".paginacaoControle");
        this.elPaginacaoItens.innerHTML = "";
    }

    async controleScrool(){
        this.atualScrollTop = this.elPaginacaoItens.scrollTop;

        if (this.scroolPraCima()){
            this.paginaAtual -=1;
            await this.atualizarHtmlCima();

        }else if (this.scroolPraBaixo()){
            this.paginaAtual += 1;
            await this.atualizarHtmlBaixo();

        }else{
            this.definirPaginaAtual();
        }

        this.ultimoScroolTop = this.atualScrollTop;
    }

    definirPaginaAtual(){
        console.log("define")
        var aux = [...this.elPaginacaoItens.children].filter(e => e.getBoundingClientRect().bottom >= 0 && e.getBoundingClientRect().top <= this.elPaginacaoItens.getBoundingClientRect().height);
        var pgAtualEl = +aux[aux.length-1].getAttribute("paginaatual")

        if (pgAtualEl != this.paginaAtual && !this.scrollComeco && !this.scrollFim){
            this.paginaAtual = pgAtualEl;
            this.atualizarPaginacao();
            console.log('atual', this.paginaAtual)
        }
    }

    scroolPraCima(){
        if (this.atualScrollTop < this.ultimoScroolTop
            && !this.scrollComeco
            && this.paginaAtual > 1
            && this.elPaginacaoItens.scrollTop < this.distanciaCarregar
        ){
            this.scrollComeco = true;
            return true;
        }

        return false;
    }
    
    scroolPraBaixo(){
        if (this.atualScrollTop > this.ultimoScroolTop    
            && !this.scrollFim
            && this.paginaAtual < this.qtdPaginas
            && Math.abs(this.elPaginacaoItens.scrollHeight - this.elPaginacaoItens.clientHeight - this.elPaginacaoItens.scrollTop) < this.distanciaCarregar
        ){
            this.scrollFim = true;
            return true;
        }

        return false;
    }

    async atualizarHtmlCima(mover=false, qtdlimpar=0){
        console.log('ok cima');
        
        const previousScrollHeight = this.elPaginacaoItens.scrollHeight;
        const previousScrollTop = this.elPaginacaoItens.scrollTop;

        var auxLimpar = 0;

        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]')){
            this.elPaginacaoItens.prepend(...await this.retornarRangeElementos());

            const newScrollHeight = this.elPaginacaoItens.scrollHeight;
            this.elPaginacaoItens.scrollTop = previousScrollTop + (newScrollHeight - previousScrollHeight) - this.distanciaCarregar / 2;

            if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3){
                auxLimpar = this.elPaginacaoItens.children.length-(this.elPaginacaoItens.children.length-this.qtdElPorPagina*2+1);
            }
        }

        var tempo = 0;
        if (mover){
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel){
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
            tempo = this.limparAoCarregar ? 1000 + this.tempoEspera : this.tempoEspera;
        }

        setTimeout(() => {
            if (this.limparAoCarregar && (auxLimpar > 0 || qtdlimpar != 0)){
                for (let i = this.elPaginacaoItens.children.length-1; i > auxLimpar; i--){
                    this.elPaginacaoItens.children[i].remove();
                }
            }

            this.atualizarPaginacao();

            this.scrollComeco = false;
        }, tempo);
    }

    async atualizarHtmlBaixo(mover=false, qtdlimpar=0){
        console.log('ok baixo');

        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]')){
            this.elPaginacaoItens.append(...await this.retornarRangeElementos());
        }

        var tempo = 0;
        if (mover){
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel){
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
            tempo = this.limparAoCarregar ? 1000 + this.tempoEspera : this.tempoEspera;
        }

        setTimeout(() => {
            if (this.limparAoCarregar && (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3 || qtdlimpar > 0)){
                var auxLimpar = this.qtdElPorPagina-1;
                if (qtdlimpar > 0){
                    auxLimpar = qtdlimpar-1;
                }
                for (let i = auxLimpar; i >= 0; i--){
                    this.elPaginacaoItens.children[i].remove();
                }
            }

            this.atualizarPaginacao();
            this.scrollFim = false;
        }, tempo);
    }

    async irParaPagina(pagina, posScrool=0){
        console.log("irpagina", pagina)
        
        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + pagina + '"]')){
            if (pagina > this.paginaAtual){
                var qtditenslimpar = this.elPaginacaoItens.children.length;
                if (this.paginaAtual + 1 == pagina){
                    qtditenslimpar = 0;
                }
                this.paginaAtual = pagina;
                this.atualizarHtmlBaixo(true, qtditenslimpar);
            }else{
                var qtditenslimpar = this.elPaginacaoItens.children.length;
                if (this.paginaAtual - 1 == pagina){
                    qtditenslimpar = 0;
                }
                this.paginaAtual = pagina;
                this.atualizarHtmlCima(true, qtditenslimpar);
            }
        }else{
            this.paginaAtual = pagina;
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel){
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
        }
    }

    toggleCarregando(){
        var carregando = this.elPaginacaoItens.querySelector(".msgTela");
        if (carregando){
            carregando.remove();
        }else{
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", '<div class="msgTela">Carregando...</div>');
        }
    }

    toggleErro(msg){
        var erro = this.elPaginacaoItens.querySelector(".msgTela");
        if (erro){
            erro.remove();
        }else{
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", `<div class="msgTela" style="color: red;">${msg}</div>`);
        }
    }

    async retornarRangeElementos(){
        const tempoInicio = performance.now();
        this.tempoEspera = 0;

        var take = this.paginaAtual * this.qtdElPorPagina;
        var skip = this.qtdElPorPagina+take - this.qtdElPorPagina*2;
        
        console.log(this.paginaAtual, skip, take, this.qtdElPorPagina)

        this.filtros['limit'] = this.qtdElPorPagina;
        this.filtros['skip'] = skip;
        this.filtros['qtdItens'] = this.qtdTotalElementos;
        this.filtros['paginaAtual'] = this.paginaAtual == 0 ? 1 : this.paginaAtual;

        if (this.filtros.checkLivros){
            this.conteudoHtml = conteudoHtmlLivro;
        }else if (this.filtros.checkLeitores || this.filtros.checkAutores || this.filtros.checkEditoras){
            this.conteudoHtml = conteudoHtmlUsuario;
        }else if (this.filtros.checkPublicacoes){
            this.conteudoHtml = conteudoHtmlPublicacao;
        }

        this.filtros.primeiroretorno = false;

        this.toggleCarregando();

        const response = await fetch('/pesquisa', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(this.filtros)
        });

        var resposta = await response.json()
        var retorno = [];

        console.log('r', resposta)

        if (resposta.erro != ""){
            this.toggleCarregando();
            this.toggleErro(resposta.erro);
            return retorno;
        }

        for (var dado of resposta.dados){
            var innerAux = this.conteudoHtml(dado)
            var da = document.createElement('div');
            if (innerAux.trim().startsWith("<a")){
                da = document.createElement('a');
            }
            
            da.innerHTML = innerAux;
            var antes = da.querySelector(':first-child');
            if (antes != null){
                Array.from(antes.attributes).forEach(attr => {
                    da.setAttribute(attr.name, attr.value);
                });
                da.innerHTML = antes.innerHTML;
            }
            da.setAttribute("paginaatual", this.paginaAtual)
            retorno.push(da)
        }

        this.toggleCarregando();

        console.log('terminou carregar', this.scrollFim)

        this.tempoEspera = performance.now() - tempoInicio;

        return retorno;
    }

    atualizarPaginacao(){
        this.atualizarEstruturaPaginacao();
        return
        this.paginacaoControle.querySelector(".paginacaoControleNumeracao").innerHTML = `
            Página ${this.paginaAtual} de ${this.qtdPaginas} Mostrando 0 de ${this.qtdTotalElementos}
            <input type="number">
        `;
    }

    atualizarEstruturaPaginacao(){
        var pagbtns = this.paginacaoControle.querySelector(".paginacaoControleBotoes");
        pagbtns.innerHTML = "";
        pagbtns.appendChild(this.criarBtnPagina('moveresquerda'));
        console.log('attt', this.paginaAtual)
        for (var c=1; c<=this.qtdPaginas; c++){
            pagbtns.appendChild(this.criarBtnPagina(c, this.paginaAtual == c));
        }
        pagbtns.appendChild(this.criarBtnPagina('moverdireita'));
    }

    criarBtnPagina(texto, selecionado=false){
        var btn = document.createElement("button");
        btn.classList.add("btnPagina");
        if (texto == "moveresquerda"){
            btn.classList.add("mover");
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5H1m0 0 4 4M1 5l4-4"></path></svg>';
            btn.addEventListener("click", async (e) =>{
                if (this.paginaAtual > 1 && !this.scrollComeco){
                    this.scrollComeco = true;
                    console.log('click  vooltar')
                    this.paginaAtual -=1;
                    await this.atualizarHtmlCima(true);
                    this.definirPaginaAtual();
                }
            });

        }else if (texto == "moverdireita"){
            btn.classList.add("mover");
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"></path></svg>'
            btn.addEventListener("click", async (e) =>{
                console.log("click andar", this.scrollFim)
                if (this.paginaAtual < this.qtdPaginas && !this.scrollFim){
                    this.scrollFim = true;
                    console.log('click  andar')
                    this.paginaAtual += 1;
                    await this.atualizarHtmlBaixo(true);
                    this.definirPaginaAtual();
                }
            });

        }else{
            if (selecionado){
                btn.classList.add("selecionado");
            }
            btn.setAttribute("pagina", texto);
            btn.innerHTML = texto;
            btn.addEventListener("click", async (e) =>{
                this.irParaPagina(+texto)
            });
        }

        return btn;
    }

    atualizarTamanho(){
        this.el.style.height = window.innerHeight - this.el.getBoundingClientRect().top - 1 + "px";
        this.atualizarEstruturaPaginacao();
    }
}
