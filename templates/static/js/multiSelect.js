
class MultiploSelect{
    constructor(id, valores){
        if (typeof id == "string"){
            id = document.getElementById(id);
        }

        if (id == null){
            id = document.createElement("div");
            document.body.appendChild(id);
        }

        id.classList.add("multiselect");
        id.innerHTML = `<input name="campo${id.id.charAt(0).toUpperCase() + id.id.slice(1)}" readonly>`;

        this.el = id;
        this.valores = valores;
        this.campo = this.el.querySelector("input");
        this.container = document.createElement("div");
        this.criarItens();

        this.atualizarTamanho();
        window.addEventListener("resize", this.atualizarTamanho.bind(this));
        this.selecionarPreferencias();
    }

    criarItens(){
        this.container.classList.add("multiselectitens");
        for (var valor of this.valores){
            var opcao = document.createElement("div");
            opcao.innerHTML = valor;
            this.container.appendChild(opcao);
            opcao.addEventListener('click', function() {
                this.classList.toggle('selecionado');

                var input = this.closest(".multiselect").querySelector("input");
                input.value = [...this.closest(".multiselectitens").getElementsByTagName('div')].filter(e => e.classList.contains('selecionado')).map(e => e.innerHTML).join("; ");
            });
        }
        this.el.appendChild(this.container);

        this.campo.addEventListener('focus', () =>{
            if (!this.container.classList.contains("aberto")){
                this.container.classList.add("aberto");
                this.container.style.height = "max-content";
                this.atualizarTamanho();
            }
            this.abriu = true;
        })

        this.campo.addEventListener('focusout', () =>{
            console.log(lastClickedElement)
            if (lastClickedElement.closest(".multiselect") == null){
                this.container.classList.remove("aberto");
            }else if (lastClickedElement != this.campo){
                this.campo.focus();
                this.abriu = false;
            }
        })

        this.campo.addEventListener('click', () =>{
            if (this.container.classList.contains("aberto") && !this.abriu){
                this.container.classList.remove("aberto");
                this.campo.blur();
            }
            this.abriu = false;
        })
    }

    atualizarTamanho(){
        if (!this.container.classList.contains("aberto")){
            return;
        }

        this.container.style.width = this.el.getBoundingClientRect().width + "px";
        
        var alturaMenu = 0;
        var menu_ = document.getElementById("menu")
        if (menu_ != null){
            alturaMenu = menu_.getBoundingClientRect().height;
        }
        

        if (this.el.getBoundingClientRect().top >= window.innerHeight - this.el.getBoundingClientRect().bottom){
            
            if (this.container.getBoundingClientRect().height >= this.el.getBoundingClientRect().top){
                this.container.style.height = this.el.getBoundingClientRect().top - 10 - alturaMenu + "px";
                this.container.style.top = window.scrollY + 10 + "px"
            }else{
                this.container.style.top = this.el.getBoundingClientRect().top - this.container.getBoundingClientRect().height + window.scrollY;
            }
            
        }else{

            this.container.style.top = this.el.getBoundingClientRect().bottom + window.scrollY - alturaMenu + 5 + "px";

            if (this.container.getBoundingClientRect().bottom >= window.innerHeight){
                this.container.style.height = (window.innerHeight - this.container.getBoundingClientRect().top) - 10 + "px";
            }
        }
    }

    selecionarPreferencias(preferencias=[]){
        var valores = [];
        if (!preferencias || preferencias.length == 0){
            valores = this.el.getAttribute("value").trim().split(";");

        }else if (typeof preferencias == "string"){
            valores = preferencias.trim().split(";")
        }

        for (var valor of valores){
            if (valor.trim() == ""){
                continue;
            }

            for (var e of this.container.children){
                if (e.innerText == valor){
                    e.classList.add("selecionado")
                }
            }
        }

        this.el.querySelector("input").value = valores.join("; ")
    }
}

document.addEventListener("mousedown", (event) => {
    lastClickedElement = event.target;
});

var style = document.createElement('style');
style.textContent = `
    .multiselect {
        width: 100%;
    }

    .multiselect > *{
        width: 100%;
    }

    .multiselect .multiselectitens{
        position: absolute;
        display: none;
        background-color: var(--corFundo);
        overflow-y: auto;
        border: 2px solid var(--corDestaque);
        border-radius: 2px;
        padding: 2px;
        z-index: 999;
    }

    .multiselect .multiselectitens.aberto{
        display: block;
    }

    .multiselect .multiselectitens div{
        padding: 3px;
        margin-top: 2px;
        margin-bottom: 2px;
        border-radius: 5px;
    }

    .multiselect .multiselectitens div:hover{
        background-color: var(--corHover);
    }

    .multiselect .multiselectitens div.selecionado{
        background-color: var(--corSelecionado);
    }
`;
document.head.appendChild(style);