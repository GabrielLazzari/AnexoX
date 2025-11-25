class SelecionarLivro {
    static get toolbox() {
        return {
            title: 'Livro',
            icon: '<svg width="18" height="18" viewBox="0 0 512 512"><rect x="32" y="96" width="64" height="368" rx="16" ry="16" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M112 224h128M112 400h128"/><rect x="112" y="160" width="128" height="304" rx="16" ry="16" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><rect x="256" y="48" width="96" height="416" rx="16" ry="16" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><path d="M422.46 96.11l-40.4 4.25c-11.12 1.17-19.18 11.57-17.93 23.1l34.92 321.59c1.26 11.53 11.37 20 22.49 18.84l40.4-4.25c11.12-1.17 19.18-11.57 17.93-23.1L445 115c-1.31-11.58-11.42-20.06-22.54-18.89z" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/></svg>'
        };
    }

    static get isReadOnlySupported() {
        return !0
    }

    static get sanitize() {
        return {
            value: true
        };
    }

    constructor({ data, api, config, readOnly }) {
        this.data = {
            value: data.value || 'Clique para escolher um livro'
        };
        this.readOnly = readOnly;
        this.wrapper = null;
        if (window.location.pathname == "/usuario"){
            this.readOnly = true;
        }
        if (!this.readOnly){
            this.escolherLivro();
        }
    }

    render() {
        this.wrapper = document.createElement('div');
        this.wrapper.classList.add('select-plugin-wrapper');
        this.wrapper.classList.add('select-plugin-livro');

        if (!this.readOnly) {
            this.clicou = false;
            console.log("aaaaaqqq 1")
            this.wrapper.addEventListener('click', () => {
                console.log("aaaaaqqq 2")
                this.escolherLivro();
                this.clicou = true;
            });
            if (!this.clicou && this.data.value.includes("livroSelecionadoPublicacao")){
                this.wrapper.innerHTML = this.data.value;
                this.data.value = this.construirHtml(this.data.value, this.wrapper.querySelector(".livroSelecionadoPublicacao").getAttribute("idlivro"));
            }

        }else{
            this.wrapper.innerHTML = this.data.value;
        }
        return this.wrapper;
    }

    escolherLivro(){
        if (this.readOnly){
            return;
        }
        this.objPag = null;

        if (typeof abrirSobreTela !== 'function'){
            return;
        }

        abrirSobreTela('sobretelaEscolherLivro');
        if (this.objPag == null) {
            this.objPag = new Paginacao("#areaEscolherLivro", {
                url: '/pesquisaLivros',
                conteudoHtml: conteudoHtmlLivroPesquisa,
                mostrarBarraPesquisa: true,
                clickItem: (item) => {
                    this.wrapper.innerHTML = item.outerHTML;
                    this.wrapper.firstChild.className = "livroSelecionadoPublicacao";
                    this.wrapper.firstChild.removeAttribute("paginaatual");

                    this.construirHtml(item.innerHTML, item.getAttribute("idlivro"))
                    fecharSobreTela('sobretelaEscolherLivro', true);
                }
            });
        }
    }

    construirHtml(conteudo, idLivro) {
        var elLink = document.createElement("a");
        elLink.className = "livroSelecionadoPublicacao";
        elLink.href = "livro?id=" + idLivro;
        elLink.target = "_blank";
        elLink.innerHTML = conteudo;
        this.data.value = elLink.outerHTML;
        return elLink.outerHTML;
    }

    save() {
        return { value: this.data.value };
    }
}