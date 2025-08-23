var conteudo = document.getElementById("conteudo");
var elementosMovimentarTeclado = [];

var btnMenu = document.getElementById("btnMenu");
var btnInicio = document.getElementById("btnInicio");
var btnUsuario = document.getElementById("btnUsuario");
var btnFeed = document.getElementById("btnFeed");
var btnNotificacoes = document.getElementById("btnNotificacoes");

var barraPesquisa = document.getElementById("barraPesquisa");
var btAbrirFiltros = document.getElementById("btAbrirFiltros");
var campoPesquisa = document.getElementById("campoPesquisa");
var caixaPesquisa = document.getElementById("caixaPesquisa");
var resultadoPesquisa = document.getElementById("resultadoPesquisa");
var resultadoLivros = document.getElementById("resultadoLivros");
var resultadoUsuario = document.getElementById("resultadoUsuario");
var caixaFiltro = document.getElementById("caixaFiltro");

var menuSuspenso = document.getElementById("menuSuspenso");

var pesquisa_livros_sugeridos = [];
var pesquisa_usuarios_sugeridos = [];

function atualizarMenu(){
    if (window.innerWidth < 450 && window.getComputedStyle(btnInicio).getPropertyValue("display") == "block"){
        menuSuspenso.classList.remove("aberto");
        btnInicio.style.display = "none";
        btnUsuario.style.display = "none";
        btnFeed.style.display = "none";
        btnNotificacoes.style.display = "none";

    }else if (window.innerWidth >= 450 && window.getComputedStyle(btnInicio).getPropertyValue("display") == "none"){
        btnInicio.style.display = "block";
        btnUsuario.style.display = "block";
        btnFeed.style.display = "block";
        btnNotificacoes.style.display = "block";
    }
}

function atualizarTamanhoCaixaPesquisa(){
    if (window.innerWidth < 450){
        caixaPesquisa.style.width = document.documentElement.clientWidth - 20 + "px";
        caixaPesquisa.style.left = "0px";
    }else{
        caixaPesquisa.style.width = window.getComputedStyle(barraPesquisa).getPropertyValue("width");
        caixaPesquisa.style.left = barraPesquisa.getBoundingClientRect().left -10 + "px";
    }

    if (pesquisa_livros_sugeridos.length > 1){
        if (window.innerWidth < 600){
            pesquisa_livros_sugeridos[1].style.display = "none";
            if (pesquisa_usuarios_sugeridos.length > 2){
                pesquisa_livros_sugeridos[2].style.display = "none";
            }
        }else if (window.innerWidth < 800 && pesquisa_livros_sugeridos.length > 2){
            pesquisa_livros_sugeridos[1].style.display = "flex";
            pesquisa_livros_sugeridos[2].style.display = "none";
        }else if (window.innerWidth >= 800 && pesquisa_livros_sugeridos.length > 2){
            pesquisa_livros_sugeridos[2].style.display = "flex";
        }else if (window.innerWidth >= 600){
            pesquisa_livros_sugeridos[1].style.display = "flex";
        }
    }

    if (pesquisa_usuarios_sugeridos.length > 1){
        if (window.innerWidth < 600){
            pesquisa_usuarios_sugeridos[1].style.display = "none";
            if (pesquisa_usuarios_sugeridos.length > 2){
                pesquisa_usuarios_sugeridos[2].style.display = "none";
            }
        }else if (window.innerWidth < 800 && pesquisa_usuarios_sugeridos.length > 2){
            pesquisa_usuarios_sugeridos[1].style.display = "flex";
            pesquisa_usuarios_sugeridos[2].style.display = "none";
        }else if (window.innerWidth >= 800 && pesquisa_usuarios_sugeridos.length > 2){
            pesquisa_usuarios_sugeridos[2].style.display = "flex";
        }else if (window.innerWidth >= 600){
            pesquisa_usuarios_sugeridos[1].style.display = "flex";
        }
    }

    caixaPesquisa.style.top = barraPesquisa.getBoundingClientRect().bottom + 2 + "px";
}

function atualizarTamanhoCaixaFiltros(){
    if (window.innerWidth < 450){
        caixaFiltro.style.width = document.documentElement.clientWidth - 20 + "px";
        caixaFiltro.style.left = "0px";
    }else{
        caixaFiltro.style.left = barraPesquisa.getBoundingClientRect().left -10 + "px";
    }

    caixaFiltro.style.top = barraPesquisa.getBoundingClientRect().bottom + 2 + "px";
    if (caixaFiltro.getBoundingClientRect().bottom > window.innerHeight){
        caixaFiltro.style.height = window.innerHeight - caixaFiltro.getBoundingClientRect().top + "px";
    }else{
        caixaFiltro.style.height = "max-content";
    }
}

function abrirSobreTela(sobreTela, btn=null){
    if (typeof sobreTela === "string"){
        sobreTela = document.getElementById(sobreTela)
    }
    
    if (sobreTela == null){
        return;
    }

    sobreTela.classList.add("aberto");
    atualizarMovimentacaoTeclado(sobreTela.id);

    if (sobreTela.id == "caixaPesquisa"){
        caixaFiltro.classList.remove("aberto");
        atualizarTamanhoCaixaPesquisa();

    }else if (sobreTela.id == "caixaFiltro"){
        caixaPesquisa.classList.remove("aberto");
        atualizarTamanhoCaixaFiltros();

    }else if (sobreTela.id == "caixaNotificacoes"){
        abrirNotificacoes();
    }

    if (btn != null){
        sobreTela.style.top = btn.getBoundingClientRect().bottom + "px";
    }
}

function fecharSobreTela(sobreTela, obrigarFechamento=false){
    if (sobreTela){
        if (typeof sobreTela === "string"){
            sobreTela = document.getElementById(sobreTela)
        }

    }else{
        sobreTela = document.querySelector(".sobreTela.aberto");
    }

    if (sobreTela){
        if (obrigarFechamento || 
                event.target.classList.contains("modal") || 
                (!event.target.closest("#"+sobreTela.id)
                    && (sobreTela.id != "caixaFiltro" && sobreTela.id != "caixaPesquisa"
                        || (sobreTela.id == "caixaFiltro" && (!event.target.closest("#btAbrirFiltros") || document.activeElement != btAbrirFiltros))
                        || (sobreTela.id == "caixaPesquisa" && (!event.target.closest("#campoPesquisa") || document.activeElement != campoPesquisa))
                    )
                
                )
            ){
                    
            sobreTela.classList.remove("aberto");
            atualizarMovimentacaoTeclado('inicio');
            if (sobreTela.id == "sobretelaInfoLista"){
                var sobretelaSelecionarListaLivro = document.getElementById("sobretelaSelecionarListaLivro");
                if (sobretelaSelecionarListaLivro){
                    sobretelaSelecionarListaLivro.classList.remove("aberto");
                }
                var sobretelaGerenciarLista = document.getElementById("sobretelaGerenciarLista");
                if (sobretelaGerenciarLista){
                    sobretelaGerenciarLista.classList.remove("aberto");
                }
            }
        }
    }
}

function retornarInofrmacoesEmComum(){
    return retornarFiltrosPesquisa();
}

function abrirNotificacoes(){
    var menu = document.getElementById("menu");
    var caixaNotificacoes = document.getElementById('caixaNotificacoes');
    caixaNotificacoes.style.top = menu.getBoundingClientRect().bottom + "px"
}

campoPesquisa.addEventListener("keyup", (event) => {
    if (event.key == "Enter"){
        executarPesquisa();
    }else {
        obterSugestaoNomes(campoPesquisa.value.trim());
    }
});

campoPesquisa.addEventListener("focusin", (event) => {
    abrirSobreTela("caixaPesquisa");
});

var btAbrirFiltrosFoco = false;
btAbrirFiltros.addEventListener("focusin", (event) => {
    btAbrirFiltrosFoco = true;
    abrirSobreTela("caixaFiltro");
});

btAbrirFiltros.addEventListener("click", (event) => {
    if (!btAbrirFiltrosFoco){
        if (caixaFiltro.classList.contains("aberto")){
            caixaFiltro.classList.remove("aberto");
            atualizarMovimentacaoTeclado('inicio');
        }else{
            abrirSobreTela(caixaFiltro);
        }
    }
    btAbrirFiltrosFoco = false;
});

btnMenu.addEventListener("click", (event) => {
    abrirSobreTela("menuSuspenso");
});

function atualizarMovimentacaoTeclado(tela){
    if (tela == "inicio"){
        telaAtiva = [];
        elementosMovimentarTeclado = [btnMenu, btnInicio, btnUsuario, btnNotificacoes];
    }else if (tela == "caixaFiltro"){
        elementosMovimentarTeclado = [...caixaFiltro.querySelectorAll('input:enabled:not([hidden]):not([style*="display: none"]), button:enabled:not([style*="display: none"]), a:enabled:not([style*="display: none"])')];
    }else if (tela == "caixaPesquisa"){
        elementosMovimentarTeclado.push(campoPesquisa);
        elementosMovimentarTeclado.push(...caixaPesquisa.querySelectorAll('input:enabled:not([hidden]):not([style*="display: none"]), button:enabled:not([style*="display: none"]), a:enabled:not([style*="display: none"])'));
        pesquisa_livros_sugeridos = caixaPesquisa.getElementsByClassName("previewPesquisaLivro");
        pesquisa_usuarios_sugeridos = caixaPesquisa.getElementsByClassName("previewPesquisaUsuario");
    }else if (tela == "menuSuspenso"){
        elementosMovimentarTeclado = [...menuSuspenso.querySelectorAll('input:enabled:not([hidden]):not([style*="display: none"]), button:enabled:not([style*="display: none"]), a:enabled:not([style*="display: none"])')];
    }
}

function executarMovimentacaoTeclado(tecla) {
    const atual = document.activeElement || elementosMovimentarTeclado[0];
    const rectAtual = atual.getBoundingClientRect();

    let elSelecionar = null;
    let menorDistancia = Infinity;
    
    //console.log("============================")

    elementosMovimentarTeclado.forEach(el => {
        if (el === atual) return;

        const rect = el.getBoundingClientRect();
        const dx = rect.left - rectAtual.left;
        const dy = rect.top - rectAtual.top;

        //console.log(dx, dy, el.id || el.innerText)

        let valido = false;
        let distancia = Infinity;

        switch (tecla) {
            case 'w': // cima
                valido = dy < 0;
                break;
            case 's': // baixo
                valido = dy > 0;
                break;
            case 'a': // esquerda
                valido = dx < 0;
                break;
            case 'd': // direita
                valido = dx > 0;
                break;
        }

        if (valido) {
            if (tecla === 'w' || tecla === 's') {
                //console.log('da', Math.abs(dy) + Math.abs(dx))
                distancia = Math.abs(dy) + Math.abs(dx*2) + (Math.abs(dy) + Math.abs(dx));
            } else {
                //console.log('db', Math.abs(dx) + Math.abs(dy))
                distancia = Math.abs(dx) + Math.abs(dy*2) + (Math.abs(dy) + Math.abs(dx));
            }
            
            //console.log('d', distancia)

            if (distancia < menorDistancia) {
                menorDistancia = distancia;
                if (atual.getAttribute("type") == "radio"){
                    event.preventDefault()
                }
                elSelecionar = el;
            }
        }
    });

    if (elSelecionar) {
        elSelecionar.focus();
    }
}

document.onmousedown = function(event){
    fecharSobreTela();
}

document.onkeydown = function(event){
    if (event.key == "ArrowUp"){executarMovimentacaoTeclado("w");}
    else if (event.key == "ArrowDown"){executarMovimentacaoTeclado("s");}
    else if (event.key == "ArrowLeft"){executarMovimentacaoTeclado("a");}
    else if (event.key == "ArrowRight"){executarMovimentacaoTeclado("d");}
    else if (event.key === "Enter"){
        if (event.target.getAttribute("type") == "checkbox" || event.target.getAttribute("type") == "radio"){
            event.target.click();
        }
    }
}

document.onkeyup = function(event){
    console.log(event.key)
    if (event.key == "Tab"){fecharSobreTela();}
    else if (event.key == "Escape"){fecharSobreTela(null, obrigarFechamento=true)}
}

window.addEventListener('resize', event =>{
    atualizarMenu();
    atualizarTamanhoCaixaPesquisa();
    atualizarTamanhoCaixaFiltros();
});

atualizarMenu();
atualizarMovimentacaoTeclado("inicio");

// Serve para preecher os campos de filtro se a tela receber os valores e tiver o elemento de id 'dataDados'
var valoresFiltro = JSON.parse(document.getElementById('dataDados')?.innerText || '{}');
function atualizarValoresCaixaFiltros(valoresFiltro){
    console.log('v', valoresFiltro);
    for (const [chave, valor] of Object.entries(valoresFiltro)){
        if (el = document.getElementById(chave)){
            if (el.type == "checkbox" || el.type == "radio"){
                el.checked = !!valor;
            }else{
                el.value = valor;
            }
        }
    }
}
atualizarValoresCaixaFiltros(valoresFiltro);




var estilosLiterarios = [
    {nome: "Romance", icone: ""},
    {nome: "Suspense", icone: ""},
    {nome: "Mistério", icone: ""},
    {nome: "Aventura", icone: ""},
    {nome: "Policial", icone: ""},
    {nome: "Ficção Científica", icone: ""},
    {nome: "Fantasia", icone: ""},
    {nome: "Técnicos / Estudos", icone: ""},
    {nome: "Bibliográficos / Auto Bibliográficos", icone: ""},
    {nome: "Terror", icone: ""},
    {nome: "Histórico", icone: ""},
    {nome: "Auto Ajuda", icone: ""},
    {nome: "Religioso", icone: ""},
    {nome: "RoFinançasmance", icone: ""},
    {nome: "Literatura", icone: ""},
    {nome: "Infanto Juvenil", icone: ""},
    {nome: "Contos", icone: ""},
    {nome: "Poesia", icone: ""}
]

function auxEstilos(){
    var estilosCadastro = ""
    for (var estilo of estilosLiterarios){
        estilosCadastro += `<span>${estilo.nome}</span>\n`
    }
    console.log(estilosCadastro)
}
//auxEstilos()


var style = document.createElement('style');
style.textContent = `
#janelaDevMode{
    position: fixed;
    top: 0;
    z-index: 999;
    user-select: none;
    pointer-events: none;
    font-family: monospace;
    left: 30px;
    border: none;
    background-color: white;
    display: none;
}
`;
document.head.appendChild(style);

var mousex = 0;
var mousey = 0;
document.onmousemove = function(event){
    mousex = event.clientX;
    mousey = event.clientY;
}

janelaDevMode = document.createElement('div');
janelaDevMode.id = "janelaDevMode";
document.body.appendChild(janelaDevMode);
function atualizarJanelaDevMode(){
    janelaDevMode.innerHTML = ` Mouse: [${mousex}, ${mousey}]`;
}

atualizarJanelaDevMode();
setInterval(atualizarJanelaDevMode, 300);