function conteudoHtmlLivro(livro){
    return `
        <div class="livroItem" onclick="paginaLivro('${livro.id}')">
            <div>
                <img class="imgLivro" src="${livro.img}">
                <div class="controles">
                    <button class="btnAnimaRotate" onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-m"></button>
                    <button class="btnAnimaRotate" onclick="salvarLivro('${livro.id}')" title="Salvar na Lista"><img src="static/icones/bookmark-outline.svg" alt="" class="svg-m"></button>
                </div>
            </div>
            <div>
                <div class="dataLabel">Título</div>
                <div class="dataContent">${livro.titulo}</div>
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
    return `
        <div class="livroItem" onclick="paginaLivro('${livro.id}')">
            <div>
                <img class="imgLivro" src="static/imagens/livros/QuatroVidasDeUmCachorro.jpg">
                <div class="controles">
                    <button class="btnAnimaRotate" onclick="removerLivroLista('${livro.id}')" title="Remover da Lista"><img src="static/icones/trash-outline.svg" alt="" class="svg-m"></button>
                    <button class="btnAnimaRotate" onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-m"></button>
                    <button class="btnAnimaRotate" onclick="moverLivro('${livro.id}')" title="Mover para Lista"><img src="static/icones/swap-horizontal-outline.svg" alt="" class="svg-m"></button>
                    <button class="btnAnimaRotate" onclick="duplicarLivro('${livro.id}')" title="Duplicar para Lista"><img src="static/icones/duplicate-outline.svg" alt="" class="svg-m"></button>
                </div>
            </div>
            <div>
                <div class="dataLabel">Título</div>
                <div class="dataContent">${livro.titulo}</div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Autor</div>
                <div class="dataContent"><a href="">${livro.autor}</a></div>
            </div>
            <hr>
            <div>
                <div class="dataLabel">Editora</div>
                <div class="dataContent"><a href="">${livro.editora}</a></div>
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
                <div>${publicacao.titulo}</div>
            </div>
            <div class="publicacaoItemComentario">
                <hr>
                <div class="comentario">
                    <img src="${publicacao.imgUsuario}">
                    <div>
                        <div class="comentarioCabecalho">
                            <div>${publicacao.nomeUsuario}</div>
                            <button class="btnMaisInfo"></button>
                        </div>
                        <div class="comentarioConteudo">
                            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Veniam perspiciatis quis tempore distinctio soluta cum obcaecati, fugit alias aliquam suscipit. Quisquam veniam aperiam ea ex qui error quos sit quae.
                        </div>
                        <div class="comentarioAcoes">
                            <button>Comentar</button>
                            <button></button>
                        </div>
                    </div>
                </div>
            </div>
        <div>
    `;
}

/*class Paginacao{
    constructor(elemento, url, conteudoHtml, qtdTotalElmentos=0, qtdElPorPagina=10){
        this.elemento = elemento;
        this.url = url;
        this.conteudoHtml = conteudoHtml;
        this.paginaAtual = 1;
        this.qtdElPorPagina = qtdElPorPagina;
        this.qtdTotalElmentos = qtdTotalElmentos;
        this.ultimoScroolTop = 0;
        this.elemento.innerHTML = "";
        this.elemento.classList.add("paginacao");
        this.elemento.insertAdjacentHTML("beforeend", '<div class="paginacaoItens"></div>');
        this.elemento.insertAdjacentHTML("beforeend", '<div class="paginacaoControle"></div>');
        this.elPaginacaoItens = this.elemento.querySelector(".paginacaoItens");
        this.paginacaoControle = this.elemento.querySelector(".paginacaoControle");
        
        if (this.elPaginacaoItens.scrollHeight <= this.elPaginacaoItens.clientHeight){
            //this.qtdElPorPagina *= 2;
        }
        this.atualizarHTML();

        this.qtdPaginas = Math.ceil(this.qtdTotalElmentos / this.qtdElPorPagina);

        this.elPaginacaoItens.addEventListener('scroll', (e) => {
            this.controleScrool();
        });

        this.atualizarTamanho();
        window.addEventListener("resize", this.atualizarTamanho.bind(this));
    }

    controleScrool(){
        const currentScrollTop = this.elPaginacaoItens.scrollTop;
        
        if (currentScrollTop > this.ultimoScroolTop) {
            if (this.elPaginacaoItens.offsetHeight + this.elPaginacaoItens.scrollTop >= this.elPaginacaoItens.scrollHeight - 150){
                console.log("proximo atual", this.paginaAtual)
                if (this.paginaAtual < this.qtdPaginas){
                    this.paginaAtual += 1;
                    this.atualizarHTML("proximo");
                }
            }
        } else if (currentScrollTop < this.ultimoScroolTop) {
            if (this.elPaginacaoItens.scrollTop <= 50){
                console.log("voltar atual", this.paginaAtual)
                if (this.paginaAtual > 1){
                    //this.paginaAtual -=1;
                    //this.atualizarHTML("voltar");
                }
            }
        }

        this.ultimoScroolTop = currentScrollTop;
    }

    atualizarTamanho(){
        this.elemento.style.height = window.innerHeight - this.elemento.getBoundingClientRect().top - 1 + "px";
    }

    atualizarHTML(direcao="proximo"){

        if (direcao == "proximo"){
            if (this.paginaAtual % 2 == 0){
                for (var c=this.qtdElPorPagina-1; c>=0; c--){
                    if (c < this.elPaginacaoItens.children.length){
                        this.elPaginacaoItens.children[c].remove();
                    }
                }
            }

            for (var dado of this.retornarRangeDados()){
                this.elPaginacaoItens.innerHTML += this.conteudoHtml(dado);
            }

        }else if (direcao == "voltar"){
            console.log('voltar')
            if (this.paginaAtual % 2 == 0){
                for (var c=this.elPaginacaoItens.children.length-1; c>=this.elPaginacaoItens.children.length-this.qtdElPorPagina; c--){
                    if (c >= 0){
                        this.elPaginacaoItens.children[c].remove();
                    }
                }
            }

            for (var dado of Array.from(this.retornarRangeDados()).reverse()){
                console.log(dado)
                this.elPaginacaoItens.innerHTML = this.conteudoHtml(dado) + this.elPaginacaoItens.innerHTML;
            }
        }
    }
    
    retornarRangeDados(){
        var take = this.paginaAtual * this.qtdElPorPagina - this.qtdElPorPagina;
        var skip = this.qtdElPorPagina;
        
        filtros = retornarFiltrosPesquisa();
        filtros['limit'] = take;
        filtros['skip'] = skip+take;

        fetch('/pesquisa', {
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

        return d.slice(take, skip+take);
    }
}*/

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
        console.log(Math.abs(this.elPaginacaoItens.scrollHeight - this.elPaginacaoItens.clientHeight - this.elPaginacaoItens.scrollTop) < this.distanciaCarregar )
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

        //this.paginaAtual -=1;
        this.elPaginacaoItens.prepend(...await this.retornarRangeElementos());
        //this.paginaAtual +=1;

        const newScrollHeight = this.elPaginacaoItens.scrollHeight;
        this.elPaginacaoItens.scrollTop = previousScrollTop + (newScrollHeight - previousScrollHeight);

        if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3 || this.paginaAtual==1){
            var aux = this.elPaginacaoItens.children.length-this.qtdElPorPagina-1;
            for (let i = this.elPaginacaoItens.children.length-1; i > aux; i--){
                this.elPaginacaoItens.children[i].remove();
            }
        }

        this.atualizarPaginacao();
    }

    async atualizarHtmlBaixo(){
        console.log('ok baixo');

        this.elPaginacaoItens.append(...await this.retornarRangeElementos());

        if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3){
            for (let i = this.qtdElPorPagina-1; i >= 0; i--){
                this.elPaginacaoItens.children[i].remove();
            }
        }

        this.atualizarPaginacao();
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

        console.log('f', this.filtros)

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
            retorno.push(da)
        }

        this.scrollComeco = false;
        this.scrollFim = false;
        return retorno;
    }

    atualizarPaginacao(){
        this.paginacaoControle.innerHTML = 'Pagina ' + this.paginaAtual + ' de ' + this.qtdPaginas;
    }

    atualizarTamanho(){
        this.el.style.height = window.innerHeight - this.el.getBoundingClientRect().top - 50 + "px";
    }
}
