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
    return `
        <a class="usuarioItem" href="usuario?id=${usuario.id}">
            <img class="imgLivro" src="${usuario.img}">
            <div>${usuario.nome}</div>
        <a>
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

function retornarFiltrosPesquisa(){
    infos = {};
    infos.campoPesquisa = campoPesquisa.value.trim();
    Array.prototype.forEach.call(caixaFiltro.querySelectorAll("input"), function(inp){
        infos[inp.id] = inp.checked;
    })
    
    return infos;
}

class Paginacao{
    constructor(el, filtros, qtdTotalElementos=0, qtdElPorPagina=20){
        this.el = el;
        this.filtros = filtros;
        this.conteudoHtml = '';
        this.paginaAtual = filtros['paginaAtual'] ?? 1;
        this.qtdTotalElementos = qtdTotalElementos;
        this.qtdElPorPagina = qtdElPorPagina;

        this.el.innerHTML = "";
        this.el.classList.add("paginacao");
        this.el.insertAdjacentHTML("beforeend", '<div class="paginacaoItens"></div>');
        this.el.insertAdjacentHTML("beforeend", '<div class="paginacaoControle"></div>');
        this.elPaginacaoItens = this.el.querySelector(".paginacaoItens");
        this.paginacaoControle = this.el.querySelector(".paginacaoControle");
        this.elPaginacaoItens.innerHTML = "";
        this.paginacaoControle.innerHTML = "1"

        this.distanciaCarregar = 100;
        this.scrollFim = false;
        this.scrollComeco = false;
        this.atualScrollTop = 0;
        this.ultimoScroolTop = 0;
        this.passaouPgUm = false;

        this.qtdPaginas = Math.ceil(this.qtdTotalElementos / this.qtdElPorPagina);

        this.atualizarHtmlBaixo();

        this.elPaginacaoItens.addEventListener('scroll', (e) => {
            this.controleScrool();
        });

        this.atualizarTamanho();
        window.addEventListener("resize", this.atualizarTamanho.bind(this));
    }

    controleScrool(){
        this.atualScrollTop = this.elPaginacaoItens.scrollTop;

        if (this.scroolPraCima()){
            this.paginaAtual -=1;
            this.atualizarHtmlCima();

        }else if (this.scroolPraBaixo()){
            this.paginaAtual += 1;
            this.atualizarHtmlBaixo();
        }else{
            var aux = [...this.elPaginacaoItens.children].filter(e => e.getBoundingClientRect().bottom >= 0 && e.getBoundingClientRect().top <= this.elPaginacaoItens.getBoundingClientRect().height);
            var pgAtualEl = +aux[aux.length-1].getAttribute("paginaAtual")

            if (pgAtualEl != this.paginaAtual && !this.scrollComeco && !this.scrollFim){
                this.paginaAtual = pgAtualEl;
                this.atualizarPaginacao();
            }
        }

        this.ultimoScroolTop = this.atualScrollTop;
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

    async atualizarHtmlCima(){
        console.log('ok cima');
        
        const previousScrollHeight = this.elPaginacaoItens.scrollHeight;
        const previousScrollTop = this.elPaginacaoItens.scrollTop;

        var auxLimpar = 0;

        if (!this.passaouPgUm && this.paginaAtual == 1){
            console.log('aaaaa volta inicio')
        }else{
            //this.paginaAtual -=1;
            this.elPaginacaoItens.prepend(...await this.retornarRangeElementos());
            //this.paginaAtual +=1;

            const newScrollHeight = this.elPaginacaoItens.scrollHeight;
            this.elPaginacaoItens.scrollTop = previousScrollTop + (newScrollHeight - previousScrollHeight);

            if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3){
                auxLimpar = this.elPaginacaoItens.children.length-this.qtdElPorPagina-1;
            }
        }

        if (auxLimpar > 0){
            for (let i = this.elPaginacaoItens.children.length-1; i > auxLimpar; i--){
                this.elPaginacaoItens.children[i].remove();
            }
        }


        this.atualizarPaginacao();
    }

    async atualizarHtmlBaixo(){
        console.log('ok baixo');

        if (this.paginaAtual >= 3){
            this.passaouPgUm = true;
        }

        this.elPaginacaoItens.append(...await this.retornarRangeElementos());

        if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3){
            for (let i = this.qtdElPorPagina-1; i >= 0; i--){
                this.elPaginacaoItens.children[i].remove();
            }
        }

        this.atualizarPaginacao();
    }

    toggleCarregando(){
        var carregando = this.elPaginacaoItens.querySelector(".carregando");
        if (carregando){
            carregando.remove();
        }else{
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", '<div class="carregando">Carregando...</div>');
        }
    }

    async retornarRangeElementos(){
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

        var retorno = [];
        for (var dado of await response.json()){
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
            da.setAttribute("paginaAtual", this.paginaAtual)
            retorno.push(da)
        }

        this.scrollComeco = false;
        this.scrollFim = false;

        this.toggleCarregando();

        return retorno;
    }

    atualizarPaginacao(){
        this.paginacaoControle.innerHTML = 'Pagina ' + this.paginaAtual + ' de ' + this.qtdPaginas;
    }

    atualizarTamanho(){
        this.el.style.height = window.innerHeight - this.el.getBoundingClientRect().top - 50 + "px";
    }
}
