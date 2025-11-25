function conteudoHtmlLivro(livro) {
    return `
        <div class="livroItem">
            <div style="display: none" idlivro="${livro.id}"></div>
            <div class="areaCabecalho">
                <a href="livro?id=${livro.id}"><img class="imgLivro" src="${livro.img}"></a>
                <div class="controles">
                    <button onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-mm"></button>
                    <button onclick="abrirSalvarLivro('${livro.id}', this)" title="Salvar na Lista"><img src="static/icones/bookmark-outline.svg" alt="" class="svg-mm"></button>
                    <button onclick="compartilharLivroPublicar(${livro.id})"><img src="static/icones/arrow-redo-outline.svg" class="svg-mm"></button>
                </div>
            </div>
            <div class="titulo"><a href="livro?id=${livro.id}">${livro.titulo}</a></div>
            <hr>
            <div class="autor">
                <div class="dataLabel">Autor</div>
                <div class="dataContent"><a href="usuario?id=${livro.autor.id}">${livro.autor.nome}</a></div>
            </div>
            <hr>
            <div class="editora">
                <div class="dataLabel">Editora</div>
                <div class="dataContent"><a href="usuario?id=${livro.editora.id}">${livro.editora.nome}</a></div>
            </div>
        </div>
    `;
}

function conteudoHtmlLivroUsuario(livro) {
    var idUsuario = document.getElementById('idUsuario')?.innerText;

    var controles = ``;

    console.log('aaaaa', idUsuario, livro.usuario_id)

    if (idUsuario == livro.usuario_id) {
        controles = `
            <div class="controles">
                <button onclick="removerLivroLista('${livro.idRelacao}', '${livro.id}', '${livro.idLista}', this)" title="Remover da Lista"><img src="static/icones/trash-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="abrirMoverLivro('${livro.id}', '${livro.idLista}', this)" title="Mover para Lista"><img src="static/icones/swap-horizontal-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="abrirDuplicarLivro('${livro.id}', '${livro.idLista}', this)" title="Duplicar para Lista"><img src="static/icones/duplicate-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="compartilharLivroPublicar(${livro.id})" title="Criar Publicação"><img src="static/icones/arrow-redo-outline.svg" class="svg-mm"></button>
            </div>
        `;
    } else {
        controles = `
            <div class="controles">
                <button onclick="compartilharLivro('${livro.id}')" title="Compartilhar"><img src="static/icones/share-social-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="abrirSalvarLivro('${livro.id}', this)" title="Salvar na Lista"><img src="static/icones/bookmark-outline.svg" alt="" class="svg-mm"></button>
                <button onclick="compartilharLivroPublicar(${livro.id})"><img src="static/icones/arrow-redo-outline.svg" class="svg-mm"></button>
            </div>
        `;
    }

    return `
        <div class="livroItem" href="livro?id=${livro.id}">
            <div style="display: none" idlivro="${livro.id}"></div>
            <div class="areaCabecalho">
                <a href="livro?id=${livro.id}"><img class="imgLivro" src="${livro.img}"></a>
                ${controles}
            </div>
            <div class="titulo"><a href="livro?id=${livro.id}">${livro.titulo}</a></div>
            <hr>
            <div class="autor">
                <div class="dataLabel">Autor</div>
                <div class="dataContent"><a href="usuario?id=${livro.autor.id}">${livro.autor.nome}</a></div>
            </div>
            <hr>
            <div class="editora">
                <div class="dataLabel">Editora</div>
                <div class="dataContent"><a href="usuario?id=${livro.editora.id}">${livro.editora.nome}</a></div>
            </div>
        </div>
    `;
}

function conteudoHtmlLivroPesquisa(livro) {
    return `
        <div class="livroItem livroItemSimples" idlivro="${livro.id}">
            <div class="areaCabecalho">
                <img class="imgLivro" src="${livro.img}">
            </div>
            <div class="dataContent">${livro.titulo}</div>
        </div>
    `;
}

function conteudoHtmlUsuario(usuario) {
    var href = "";
    var tag = "div";
    //if (usuario.ativo) {
        href = `href="usuario?id=${usuario.id}"`;
        tag = "a";
    //}

    return `
        <div class="usuarioItem">
            <${tag} ${href} class="areaImg"><img class="imgUsuario" src="${usuario.img}"></${tag}>
            <div class="usuarioItemDetalhes">
                <${tag} ${href}>${usuario.nome}</${tag}>
                <div class="usuarioItemDescricao"></div>
            </div>
            <div class="usuarioItemAcoes">
                <button class="btnAcao" onclick="controleSeguirUsuario(${usuario.id}, this)">${usuario.seguindo ? 'Deixar de Seguir' : 'Seguir'}</button>
                <!--${href == '' ? '' : '<button class="btnAcao usuarioItemConversar"><img src="static/icones/chatbubbles-outline.svg" class="svg-sm"> Conversar</button>'}-->
                ${usuario.seguidor ? '<div class="textoSegue">Segue você</div>' : ''}
            </div>
        </div>
    `;
}

function conteudoHtmlPublicacao(publicacao) {
    var caminhoImgUsuario = document.getElementById("caminhoImgUsuario").innerHTML;
    var mostrarMaisInfo = false;
    var idUsuarioLogado = document.getElementById("idUsuarioLogado").innerText;
    if (idUsuarioLogado == publicacao.usuario.id || window.location.pathname == "/usuario"){
        mostrarMaisInfo = true;
    }

    return [`
        <div class="publicacaoItem">
            <input type="hidden" idpublicacao="${publicacao.id}">
            <div class="publicacaoItemCabecalho">
                <a href="usuario?id=${publicacao.usuario.id}"><img src="${publicacao.usuario.img}"></a>
                <div>
                    <a href="usuario?id=${publicacao.usuario.id}"><div class="publicacaoNomeUsuario">${publicacao.usuario.nome}</div></a>
                    <div class="datahora">${publicacao.data} as ${publicacao.hora}</div>
                </div>
                ${mostrarMaisInfo ? '<button class="btnMaisInfo" onclick="abrirInfoPublicacao(this)"></button>' : ''}
            </div>
            <div class="publicacaoItemConteudo">
                <div class="publicacaoConteudo"></div>
                <div class="publicacaoAcoes">
                    <button class="btnReagir ${publicacao.usuario_reagiu ? 'reagido' : ''}" onclick="reagirPublicacao(this)" title="Reagir"></button>
                    <button onclick="compartilharPublicacao(${publicacao.id})" title="Compartilhar"><img src="static/icones/arrow-redo-outline.svg" class="svg-mm"></button>
                    <button onclick="abrirSalvarPublicacao(${publicacao.id})" title="Salvar"><img src="static/icones/bookmark-outline.svg" class="svg-mm"></button>
                    <button class="btnComentarPublicacao" title="Comentar"><img src="static/icones/chatbubble-outline.svg" class="svg-mm"></button>
                </div>
            </div>
            <div class="publicacaoItemComentario">
                <hr>
                <div class="novo-comentario" style="display: none;">
                    <div class="comentario-form">
                        <img id="imgUsuarioResponder" src="${caminhoImgUsuario}">
                        <div class="comentario-input">
                            <div class="areaCheckContemSpoiler">
                                <input type="checkbox" class="checkSpoilerNovoComentario" class="checkContemSpoiler">
                                <label for="checkSpoilerNovoComentario">Contém Spoiler</label>
                            </div>
                            <div style="display: flex; align-items:baseline;">
                            <input type="text" class="input-comentario">
                            <button class="btn-enviar-comentario">Comentar</button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="areaComentarios"><div>
            </div>
        <div>`,

        function (obj) {
            new EditorJS({
                readOnly: true,
                holder: obj.querySelector(".publicacaoConteudo"),
                data: JSON.parse(publicacao.conteudo),
                tools: {
                    header: Header,
                    alert: Alert,
                    paragraph: Paragraph,
                    delimiter: Delimiter,
                    marker: Marker,
                    columns: {
                        class: editorjsColumns,
                        config: {
                            EditorJsLibrary: EditorJS
                        }
                    },
                    image: ImageTool,
                    livro: SelecionarLivro,
                    list: EditorjsList
                }
            });

            valoresFiltro = {'telaOrigem': 'publicacao', 'itemOrigemId': publicacao.id}

            new Paginacao(obj.querySelector(".areaComentarios"), {
                url: '/procurarComentarios',
                filtros: valoresFiltro,
                conteudoHtml: conteudoHtmlComentario,
                flex: false,
                qtdElPorPagina: 3,
                tipoCarregamento: 'btnMais',
                logica: function(){
                    if (this.paginaAtual == 1 && this.dados.length == 0){
                        this.toggleMsg("Nenhum comentário. Seje o primeiro(a) a comentar.");
                    }
                }
            });

            var novoComentario = obj.querySelector(".novo-comentario");
            var btnEnviar = obj.querySelector(".btn-enviar-comentario");
            btnEnviar.addEventListener('click', () => {
                if (novoComentario){
                    novoComentario.style.display = "none";
                }

                var inputComentario = obj.querySelector(".input-comentario");
                const textoComentario = inputComentario.value.trim();
                if (textoComentario) {
                    var idComentarioPai = 0;
                    var comentario = btnEnviar.closest(".comentario");
                    if (comentario){
                        var elResponder = comentario.querySelector("[idcomentariopai]");
                        if (elResponder){
                            idComentarioPai = elResponder.getAttribute("idcomentario");
                        }
                    }
                    
                    var spoiler = obj.querySelector(".checkSpoilerNovoComentario").checked;
                    comentar(obj.querySelector(".areaComentarios"), textoComentario, 'publicacao', publicacao.id, spoiler, idComentarioPai)
                    
                    inputComentario.value = '';
                }
            });

            obj.querySelector(".btnComentarPublicacao").addEventListener('click', () => {
                if (novoComentario){
                    if (novoComentario.style.display == "none"){
                        novoComentario.style.display = "block";
                    }else{
                        novoComentario.style.display = "none";
                    }
                }
            });
        }
    ];
}

function conteudoHtmlComentario(comentario) {
    console.log(comentario)
    btnSpoiler = "";
    if (comentario.spoiler) {
        btnSpoiler = `<button class="btnComentarioSpoiler" onclick="this.nextElementSibling.style.display = 'block';this.remove();">Atenção! Spoiler! Clique aqui para visualizar o comentário.</button>`;
    }

    var datahora = "";
    if (comentario.data && comentario.hora && comentario.data.toString().trim() != "" && comentario.hora.toString().trim() != ""){
        datahora = '<div class="datahora">';

        var temData = false;
        if (comentario.data && comentario.data.toString().trim() != ""){
            temData = true;
            datahora += comentario.data.toString().trim();
        }

        if (comentario.hora && comentario.hora.toString().trim() != ""){
            if (temData){ datahora += " as " }
            datahora += comentario.hora.toString().trim();
        }

        datahora += '</div>';
    }

    var idUsuarioLogado = document.getElementById("idUsuarioLogado");
    if (idUsuarioLogado){
        idUsuarioLogado = idUsuarioLogado.innerText;
    }else{
        idUsuarioLogado = 0;
    }

    return [
        `<div class="comentario ${comentario.nivel > 1 ? 'comentarioResposta' : ''}">
            <input type="hidden" idcomentario="${comentario.id}">
            <a href="usuario?id=${comentario.usuario.id}"><img src="${comentario.usuario.img}"></a>
            <div>
                <div class="comentarioCabecalho">
                    <div>
                        <a href="usuario?id=${comentario.usuario.id}"><div>${comentario.usuario.nome}</div></a>
                        ${datahora}
                    </div>
                    ${idUsuarioLogado == comentario.usuario.id ? '<button class="btnMaisInfo" onclick="abrirInfoComentario(this)"></button>' : ''}
                </div>
                ${btnSpoiler}
                <div class="comentarioConteudo" ${comentario.spoiler ? 'style="display: none"' : ''}>
                    ${comentario.conteudo}
                </div>
                <div class="comentarioAcoes">
                    <button class="btnComentar" onclick="abrirResponderComentario(this, ${comentario.origem_id}, '${comentario.origem}')">Responder</button>
                    <button class="btnReagir btnReagirComentario ${comentario.usuario_reagiu ? 'reagido' : ''}" onclick="reagirComentario(this)"></button>
                </div>
                <div class="respostas">${comentario.tem_respostas > 0 ? '<a>Mostrar Respostas</a>' : ''}</div>
            </div>
        </div>`,

        function (obj) {
            if (comentario.tem_respostas == 0) {
                return;
            }

            new Paginacao(obj.querySelector(".respostas"), {
                url: '/procurarRespostas',
                filtros: { 'idComentarioPai': comentario.id, 'telaOrigem': comentario.origem, 'itemOrigemId': comentario.origem_id },
                paginaAtual: 0,
                qtdTotalElementos: comentario.tem_respostas,
                conteudoHtml: conteudoHtmlComentario,
                flex: false,
                elScroolDeteccao: window,
                qtdElPorPagina: 5,
                tipoCarregamento: 'btnMais'
            });
        }
    ]
}

function controleSeguirUsuario(idUsuarioSeguir, btn) {
    fetch('/controleSeguirUsuario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idUsuarioSeguir: idUsuarioSeguir })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != "") {
            toast.erro(retorno.erro);
        } else {
            if (retorno.seguindo) {
                btn.innerText = "Deixar de Seguir";
            } else {
                btn.innerText = "Seguir";
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}


class Paginacao {
    constructor(el, opcoes = {}) {
        if (typeof el === "string") {
            this.el = document.querySelector(el);
        } else {
            this.el = el;
        }

        if (!this.el) {
            this.el = document.createElement("div");
        }

        const opcoesPadrao = {
            filtros: {},
            url: "",
            dados: [],
            paginaAtual: 1,  // se a pagina atual for definida como zero, nada será carregado
            qtdTotalElementos: 0,
            qtdElPorPagina: 20,
            conteudoHtml: '',
            conteudoJs: null,
            tipoCarregamento: "scrool",  // scrool, btnMais, btnPaginas
            distanciaCarregar: 100,
            limparAoCarregar: true,
            mostrarNumerosPagina: true,
            mostrarBarraPesquisa: false,
            flex: true,
            elScroolDeteccao: null
        }

        Object.assign(this, opcoesPadrao, opcoes);

        for (const chave in opcoesPadrao) {
            if (this[chave] === undefined) {
                this[chave] = opcoesPadrao[chave];
            }
        }

        this.url = this.url.trim();
        if (this.url != "" && !this.url.startsWith("/")) {
            this.url = "/" + this.url;
        }

        // configuracoes internas
        if (this.qtdTotalElementos == 0 || this.tipoCarregamento == "btnMais") {
            this.mostrarNumerosPagina = false;

        } else if (this.tipoCarregamento == "btnPaginas") {
            this.mostrarNumerosPagina = true;
        }

        console.log(this.qtdTotalElementos, this.mostrarNumerosPagina)

        this.criarEstrutura();

        this.scrollFim = false;
        this.scrollComeco = false;
        this.atualScrollTop = 0;
        this.ultimoScroolTop = 0;
        this.tempoEspera = 0;
        this.qtdElementosUltimoRetorno = 0;

        this.qtdPaginas = this.qtdTotalElementos == 0 ? 0 : Math.ceil(this.qtdTotalElementos / this.qtdElPorPagina);

        if (this.paginaAtual > 0) {
            this.atualizarHtmlBaixo();
        }

        if (this.tipoCarregamento == "scrool") {
            this.elScroolDeteccao.addEventListener('scroll', (e) => {
                this.controleScrool();
            });
        }

        if (this.elScroolDeteccao == window) {
            this.elScroolDeteccao = document.documentElement;
        }

        this.atualizarTamanho();
        this._resizeHandler = this.atualizarTamanho.bind(this);
        window.addEventListener("resize", this._resizeHandler);
    }

    criarEstrutura() {
        this.el.innerHTML = "";
        this.el.classList.add("paginacao");
        if (this.mostrarBarraPesquisa) {
            this.el.insertAdjacentHTML("beforeend", `<input class="paginacaoPesquisa" placeholder="Pesquisar...">`);
            this.paginacaoPesquisa = this.el.querySelector(".paginacaoPesquisa");
            this.pesquisaDigitando = "";
            this.paginacaoPesquisa.addEventListener("keydown", async (e) => {
                this.pesquisaDigitando = this.paginacaoPesquisa.value
            });
            this.paginacaoPesquisa.addEventListener("keyup", async (e) => {
                if (this.paginacaoPesquisa.value.trim() != "" || this.pesquisaDigitando.trim() != "") {
                    this.paginaAtual = 1;
                    this.filtros.campoPesquisa = this.paginacaoPesquisa.value;
                    this.elPaginacaoItens.innerHTML = "";
                    this.elPaginacaoItens.append(...await this.retornarRangeElementos());
                }
            });
        }

        this.el.insertAdjacentHTML("beforeend", `<div class="paginacaoItens ${this.flex ? 'paginacaoItensFlex' : ''}"></div>`);
        this.elPaginacaoItens = this.el.querySelector(".paginacaoItens");
        if (this.elScroolDeteccao == null) {
            this.elScroolDeteccao = this.elPaginacaoItens;
        }
        if (this.mostrarNumerosPagina) {
            this.el.insertAdjacentHTML("beforeend", '<div class="paginacaoControle"><div class="paginacaoControleNumeracao"></div><div class="paginacaoControleBotoes"></div></div>');
            this.paginacaoControle = this.el.querySelector(".paginacaoControle");
        } else {
            this.elPaginacaoItens.style.paddingBottom = "0px";
        }
        this.elPaginacaoItens.innerHTML = "";
        if (this.tipoCarregamento == "btnMais") {
            this.addBtnCarregarMais("Ver Respostas");
        }
    }

    limpar() {
        this.el.innerHTML = "";
        if (this._resizeHandler) {
            window.removeEventListener("resize", this._resizeHandler);
            this._resizeHandler = null;
        }
    }

    async controleScrool() {
        this.atualScrollTop = this.elScroolDeteccao.scrollTop || document.documentElement.scrollTop;

        if (this.scroolPraCima()) {
            this.paginaAtual -= 1;
            await this.atualizarHtmlCima();

        } else if (this.scroolPraBaixo()) {
            this.paginaAtual += 1;
            await this.atualizarHtmlBaixo();

        } else {
            this.definirPaginaAtual();
        }

        this.ultimoScroolTop = this.atualScrollTop;
    }

    definirPaginaAtual() {
        var aux = [...this.elPaginacaoItens.children].filter(e => e.getBoundingClientRect().bottom >= 0 && e.getBoundingClientRect().top <= this.elPaginacaoItens.getBoundingClientRect().height);
        if (aux.length > 0) {
            var pgAtualEl = +aux[aux.length - 1].getAttribute("paginaatual")

            if (pgAtualEl != this.paginaAtual && !this.scrollComeco && !this.scrollFim) {
                this.paginaAtual = pgAtualEl;
                this.atualizarPaginacao();
                console.log('atual', this.paginaAtual)
            }
        }
    }

    scroolPraCima() {
        if (this.atualScrollTop < this.ultimoScroolTop
            && !this.scrollComeco
            && (this.paginaAtual > 1)
            && this.elScroolDeteccao.scrollTop < this.distanciaCarregar
        ) {
            this.scrollComeco = true;
            return true;
        }

        return false;
    }

    scroolPraBaixo() {
        if (this.atualScrollTop > this.ultimoScroolTop
            && !this.scrollFim
            && (this.paginaAtual < this.qtdPaginas || (this.qtdPaginas == 0 && this.qtdElementosUltimoRetorno == this.qtdElPorPagina))
            && Math.abs(this.elScroolDeteccao.scrollHeight - this.elScroolDeteccao.clientHeight - this.elScroolDeteccao.scrollTop) < this.distanciaCarregar
        ) {
            this.scrollFim = true;
            return true;
        }

        return false;
    }

    async atualizarHtmlCima(mover = false, qtdlimpar = 0) {
        console.log('ok cima');

        const previousScrollHeight = this.elPaginacaoItens.scrollHeight;
        const previousScrollTop = this.elPaginacaoItens.scrollTop;

        var auxLimpar = 0;

        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]')) {
            this.elPaginacaoItens.prepend(...await this.retornarRangeElementos());

            const newScrollHeight = this.elPaginacaoItens.scrollHeight;
            this.elPaginacaoItens.scrollTop = previousScrollTop + (newScrollHeight - previousScrollHeight) - this.distanciaCarregar / 2;

            if (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3) {
                auxLimpar = this.elPaginacaoItens.children.length - (this.elPaginacaoItens.children.length - this.qtdElPorPagina * 2 + 1);
            }
        }

        var tempo = 0;
        if (mover) {
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel) {
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
            tempo = this.limparAoCarregar ? 1000 + this.tempoEspera : this.tempoEspera;
        }

        setTimeout(() => {
            if (this.limparAoCarregar && (auxLimpar > 0 || qtdlimpar != 0)) {
                for (let i = this.elPaginacaoItens.children.length - 1; i > auxLimpar; i--) {
                    this.elPaginacaoItens.children[i].remove();
                }
            }

            this.atualizarPaginacao();

            this.scrollComeco = false;
        }, tempo);
    }

    async atualizarHtmlBaixo(mover = false, qtdlimpar = 0) {
        console.log('ok baixo');

        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]')) {
            this.elPaginacaoItens.append(...await this.retornarRangeElementos());
        }

        var tempo = 0;
        if (mover) {
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel) {
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
            tempo = this.limparAoCarregar ? 1500 + this.tempoEspera : this.tempoEspera;
        }

        setTimeout(() => {
            if (this.limparAoCarregar && (this.elPaginacaoItens.children.length >= this.qtdElPorPagina * 3 || qtdlimpar > 0)) {
                var auxLimpar = this.qtdElPorPagina - 1;
                if (qtdlimpar > 0) {
                    auxLimpar = qtdlimpar - 1;
                }
                for (let i = auxLimpar; i >= 0; i--) {
                    this.elPaginacaoItens.children[i].remove();
                }
            }

            this.atualizarPaginacao();
            this.scrollFim = false;
        }, tempo);
    }

    async irParaPagina(pagina, posScrool = 0) {
        console.log("irpagina", pagina)

        if (!this.elPaginacaoItens.querySelector('[paginaatual="' + pagina + '"]')) {
            if (pagina > this.paginaAtual) {
                var qtditenslimpar = this.elPaginacaoItens.children.length;
                if (this.paginaAtual + 1 == pagina) {
                    qtditenslimpar = 0;
                }
                this.paginaAtual = pagina;
                this.atualizarHtmlBaixo(true, qtditenslimpar);
            } else {
                var qtditenslimpar = this.elPaginacaoItens.children.length;
                if (this.paginaAtual - 1 == pagina) {
                    qtditenslimpar = 0;
                }
                this.paginaAtual = pagina;
                this.atualizarHtmlCima(true, qtditenslimpar);
            }
        } else {
            this.paginaAtual = pagina;
            var primeiroel = this.elPaginacaoItens.querySelector('[paginaatual="' + this.paginaAtual + '"]');
            if (primeiroel) {
                primeiroel.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
            }
        }
    }

    toggleCarregando() {
        var carregando = this.elPaginacaoItens.querySelector(".msgTela");
        if (carregando) {
            carregando.remove();
        } else {
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", '<div class="msgTela">Carregando...</div>');
        }
    }

    toggleErro(msg) {
        var erro = this.elPaginacaoItens.querySelector(".msgTela");
        if (erro) {
            erro.remove();
        } else {
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", `<div class="msgTela" style="color: red;">${msg}</div>`);
        }
    }

    toggleMsg(msg) {
        var erro = this.elPaginacaoItens.querySelector(".msgTela");
        if (erro) {
            erro.innerHTML = msg;
        } else {
            this.elPaginacaoItens.insertAdjacentHTML("beforeend", `<div class="msgTela">${msg}</div>`);
        }
    }

    async retornarRangeElementos() {
        const tempoInicio = performance.now();
        this.tempoEspera = 0;

        if (this.tipoCarregamento == "btnMais") {
            this.btnCarregarMais = this.elPaginacaoItens.querySelector(".btnCarregarMais");
            if (this.btnCarregarMais) {
                this.btnCarregarMais.remove();
            }
        }

        var take = this.paginaAtual * this.qtdElPorPagina;
        var skip = this.qtdElPorPagina + take - this.qtdElPorPagina * 2;

        console.log(this.paginaAtual, skip, take, this.qtdElPorPagina)

        this.filtros['limit'] = this.qtdElPorPagina;
        this.filtros['skip'] = skip;
        this.filtros['qtdItens'] = this.qtdTotalElementos;
        this.filtros['paginaAtual'] = this.paginaAtual == 0 ? 1 : this.paginaAtual;

        this.filtros.primeiroretorno = false;

        this.toggleCarregando();

        this.dadosPagina = [];

        console.log(this.filtros)

        if (this.url != "") {
            const response = await fetch(this.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.filtros)
            });

            var resposta = await response.json()

            if (resposta.erro != "") {
                this.toggleCarregando();
                this.toggleErro(resposta.erro);
                return [];
            }

            this.dadosPagina = resposta.dados;
        } else {
            this.dadosPagina = this.dados;
        }

        this.qtdElementosUltimoRetorno = this.dadosPagina.length;

        this.logica();

        for (var posDado = 0; posDado < this.dadosPagina.length; posDado++) {
            let rt;
            var [innerAux, jsAux] = Array.isArray((rt = this.conteudoHtml(this.dadosPagina[posDado]))) ? rt : [rt, null];
            const match = innerAux.trim().match(/^<\s*([a-zA-Z0-9-]+)/);
            var nomeTag = match ? match[1].toLowerCase() : 'div';
            let da = document.createElement(nomeTag);

            da.innerHTML = innerAux;
            var antes = da.querySelector(':first-child');
            if (antes != null) {
                Array.from(antes.attributes).forEach(attr => {
                    da.setAttribute(attr.name, attr.value);
                });
                da.innerHTML = antes.innerHTML;
            }
            da.setAttribute("paginaatual", this.paginaAtual);
            if (jsAux) {
                jsAux(da);
            }

            if (this.clickItem) {
                da.addEventListener("click", async (e) => {
                    var aux = this.dadosPagina[posDado]
                    this.clickItem(da, aux);
                });
            }

            this.dadosPagina[posDado] = da;
        }

        if (this.dadosPagina.length > 0) {
            this.toggleCarregando();
        }

        this.tempoEspera = performance.now() - tempoInicio;

        return this.dadosPagina;
    }

    addBtnCarregarMais(texto = "Carregar Mais") {
        this.btnCarregarMais = this.elPaginacaoItens.querySelector(".btnCarregarMais");
        if (this.btnCarregarMais) {
            this.btnCarregarMais.remove();
        }

        if ((this.qtdPaginas != 0 && this.paginaAtual >= this.qtdPaginas) || this.qtdElementosUltimoRetorno < this.qtdElPorPagina) {
            return;
        }

        this.btnCarregarMais = document.createElement("button");
        this.btnCarregarMais.classList.add("btnCarregarMais");
        this.btnCarregarMais.innerHTML = texto + "<hr>";
        this.elPaginacaoItens.appendChild(this.btnCarregarMais);
        this.btnCarregarMais.addEventListener("click", async (e) => {
            if (this.paginaAtual < this.qtdPaginas && !this.scrollFim) {
                this.scrollFim = true;
                console.log('click  andar')
                this.paginaAtual += 1;
                await this.atualizarHtmlBaixo(true);
                this.definirPaginaAtual();
                this.addBtnCarregarMais();
            }
        });
    }

    logica() {
        if (this.paginaAtual == 1 && this.dadosPagina.length == 0) {
            var msg = "";
            if (this.filtros.checkLivros) { msg = "Nenhum livro encontrado"; }
            else if (this.filtros.checkLeitores) { msg = "Nenhum leitor encontrado"; }
            else if (this.filtros.checkAutores) { msg = "Nenhum autor encontrado"; }
            else if (this.filtros.checkEditoras) { msg = "Nenhuma editora encontrada"; }
            else if (this.filtros.checkPublicacoes) { msg = "Nenhuma publicação encontrada"; }
            if (this.filtros.campoPesquisa  && this.filtros.campoPesquisa != "") {
                msg += " para a pesquisa '" + this.filtros.campoPesquisa + "'";
            }
            this.toggleMsg(msg);
        }

        if (this.filtros.checkLivros) {
            this.conteudoHtml = conteudoHtmlLivro;
        } else if (this.filtros.checkLeitores || this.filtros.checkAutores || this.filtros.checkEditoras) {
            this.conteudoHtml = conteudoHtmlUsuario;
        } else if (this.filtros.checkPublicacoes) {
            this.conteudoHtml = conteudoHtmlPublicacao;
        }
    }

    //clickItem(){

    //}

    atualizarPaginacao() {
        this.atualizarEstruturaPaginacao();
        return
        this.paginacaoControle.querySelector(".paginacaoControleNumeracao").innerHTML = `
            Página ${this.paginaAtual} de ${this.qtdPaginas} Mostrando 0 de ${this.qtdTotalElementos}
            <input type="number">
        `;
    }

    atualizarEstruturaPaginacao() {
        if (!this.mostrarNumerosPagina) {
            return;
        }
        var pagbtns = this.paginacaoControle.querySelector(".paginacaoControleBotoes");
        pagbtns.innerHTML = "";
        pagbtns.appendChild(this.criarBtnPagina('moveresquerda'));
        console.log('attt', this.paginaAtual)
        for (var c = 1; c <= this.qtdPaginas; c++) {
            pagbtns.appendChild(this.criarBtnPagina(c, this.paginaAtual == c));
        }
        pagbtns.appendChild(this.criarBtnPagina('moverdireita'));
    }

    criarBtnPagina(texto, selecionado = false) {
        var btn = document.createElement("button");
        btn.classList.add("btnPagina");
        if (texto == "moveresquerda") {
            btn.classList.add("mover");
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5H1m0 0 4 4M1 5l4-4"></path></svg>';
            btn.addEventListener("click", async (e) => {
                if (this.paginaAtual > 1 && !this.scrollComeco) {
                    this.scrollComeco = true;
                    console.log('click  vooltar')
                    this.paginaAtual -= 1;
                    await this.atualizarHtmlCima(true);
                    this.definirPaginaAtual();
                }
            });

        } else if (texto == "moverdireita") {
            btn.classList.add("mover");
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"></path></svg>'
            btn.addEventListener("click", async (e) => {
                console.log("click andar", this.scrollFim)
                if (this.paginaAtual < this.qtdPaginas && !this.scrollFim) {
                    this.scrollFim = true;
                    console.log('click  andar')
                    this.paginaAtual += 1;
                    await this.atualizarHtmlBaixo(true);
                    this.definirPaginaAtual();
                }
            });

        } else {
            if (selecionado) {
                btn.classList.add("selecionado");
            }
            btn.setAttribute("pagina", texto);
            btn.innerHTML = texto;
            btn.addEventListener("click", async (e) => {
                this.irParaPagina(+texto)
            });
        }

        return btn;
    }

    atualizarTamanho() {
        if (this.tipoCarregamento == "scrool" && this.elScroolDeteccao == this.elPaginacaoItens) {
            this.el.style.height = this.el.parentElement.getBoundingClientRect().bottom - this.el.getBoundingClientRect().top+ "px";
        }
        this.atualizarEstruturaPaginacao();
    }
}
