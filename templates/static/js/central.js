var menu = document.getElementById("menu");
var conteudo = document.getElementById("conteudo");
var elementosMovimentarTeclado = [];

var btnMenu = document.getElementById("btnMenu");
var btnInicio = document.getElementById("btnInicio");
var btnUsuario = document.getElementById("btnUsuario");
var btnLivros = document.getElementById("btnLivros");
var btnFeed = document.getElementById("btnFeed");
var btnNotificacoes = document.getElementById("btnNotificacoes");
var btnAjuda = document.getElementById("btnAjuda");

var barraPesquisa = document.getElementById("barraPesquisa");
var btnLupaAbrirPesquisa = document.getElementById("btnLupaAbrirPesquisa");
var btnFiltrosAbrirFiltros = document.getElementById("btnFiltrosAbrirFiltros");
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
    if (window.innerWidth < 450 && window.getComputedStyle(btnInicio).getPropertyValue("display") == "flex"){
        menuSuspenso.classList.remove("aberto");
        btnInicio.style.display = "none";
        btnUsuario.style.display = "none";
        btnLivros.style.display = "none";
        btnFeed.style.display = "none";
        btnNotificacoes.style.display = "none";
        btnAjuda.style.display = "none";

    }else if (window.innerWidth >= 450 && window.getComputedStyle(btnInicio).getPropertyValue("display") == "none"){
        btnInicio.style.display = "flex";
        btnUsuario.style.display = "flex";
        btnLivros.style.display = "flex";
        btnFeed.style.display = "flex";
        btnNotificacoes.style.display = "flex";
        btnAjuda.style.display = "flex";
    }
}

atualizarMenu();

function atualizarTamanhoCaixaPesquisa(){
    if (window.innerWidth < 450){
        caixaPesquisa.style.width = document.documentElement.clientWidth - 20 + "px";
        caixaPesquisa.style.left = "10px";
    }else{
        caixaPesquisa.style.width = window.getComputedStyle(barraPesquisa).getPropertyValue("width");
        caixaPesquisa.style.left = barraPesquisa.getBoundingClientRect().left + "px";
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
        caixaFiltro.style.left = "10px";
    }else{
        caixaFiltro.style.left = barraPesquisa.getBoundingClientRect().left + "px";
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
        sobreTela.style.height = "max-content";
        caixaFiltro.classList.remove("aberto");
        atualizarTamanhoCaixaPesquisa();

    }else if (sobreTela.id == "caixaFiltro"){
        caixaPesquisa.classList.remove("aberto");
        atualizarTamanhoCaixaFiltros();

    }else if (sobreTela.id == "caixaNotificacoes"){
        abrirNotificacoes();

    }else if (sobreTela.id != "menuSuspenso"){
        if (btn != null){
            var distanciaTopo = btn.getBoundingClientRect().top;
            var distanciaBottom = document.documentElement.clientHeight - btn.getBoundingClientRect().bottom;
            if (distanciaBottom > distanciaTopo
                || distanciaBottom > sobreTela.getBoundingClientRect().height){
                sobreTela.style.top = btn.getBoundingClientRect().bottom + window.scrollY - btn.scrollHeight + "px";
            }else{
                if (sobreTela.getBoundingClientRect().height + 10 > distanciaTopo){
                    sobreTela.style.top = 10 + window.scrollY + "px";
                    sobreTela.style.height = distanciaTopo + "px";
                }else{
                    sobreTela.style.top = distanciaTopo - sobreTela.getBoundingClientRect().height + window.scrollY + "px";
                }
            }
            
            var distanciaEsquerda = btn.getBoundingClientRect().left;
            var distanciaDireita = document.documentElement.clientWidth - btn.getBoundingClientRect().right

            if (distanciaDireita > distanciaEsquerda || distanciaDireita > sobreTela.getBoundingClientRect().width){
                sobreTela.style.left = btn.getBoundingClientRect().right + "px"
            }else{
                if (sobreTela.getBoundingClientRect().width + 10 > distanciaEsquerda){
                    sobreTela.style.left = 10 + "px";
                    sobreTela.style.width = distanciaEsquerda + "px";
                }else{
                    sobreTela.style.left = distanciaEsquerda - sobreTela.getBoundingClientRect().width + "px";
                }
            }
        }

        if (sobreTela.classList.contains('acao')){
            sobreTela.style.height = "max-content"
            
            if (sobreTela.getBoundingClientRect().bottom > document.documentElement.clientHeight){
                sobreTela.style.height = document.documentElement.clientHeight - sobreTela.getBoundingClientRect().top - 10 + "px";
            }

            if (sobreTela.getBoundingClientRect().right > document.documentElement.clientWidth){
                sobreTela.style.width = document.documentElement.clientWidth - sobreTela.getBoundingClientRect().left - 10 + "px";
            }

            if (sobreTela.getBoundingClientRect().left < 10){
                sobreTela.style.left = "10px";
            }
        }
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
                        || (sobreTela.id == "caixaFiltro" && (!event.target.closest("#btnFiltrosAbrirFiltros") || document.activeElement != btnFiltrosAbrirFiltros))
                        || (sobreTela.id == "caixaPesquisa" && (!event.target.closest("#campoPesquisa") || document.activeElement != campoPesquisa))
                    ) && !event.target.closest("#barraPesquisa")
                )
            ){

            sobreTela.classList.remove("aberto")
            campoPesquisa.classList.remove("aberto");

            atualizarMovimentacaoTeclado('inicio');
            console.log(sobreTela.id)
            if (sobreTela.id == "sobretelaInfoLista"){
                var sobretelaSelecionarListaLivro = document.getElementById("sobretelaSelecionarListaLivro");
                if (sobretelaSelecionarListaLivro){
                    sobretelaSelecionarListaLivro.classList.remove("aberto");
                }
                var sobretelaGerenciarLista = document.getElementById("sobretelaGerenciarLista");
                if (sobretelaGerenciarLista){
                    sobretelaGerenciarLista.classList.remove("aberto");
                }
                
            }else if (sobreTela.id == "caixaPesquisa" || sobreTela.id == "caixaFiltro"){
                sobreTela.style.height = "0px";
                barraPesquisa.style.width = "30px";
                barraPesquisa.classList.remove("aberto");
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

function compartilharLivro(idLivro){
    window.location.href = "criarPublicacao?idLivro=" + idLivro;
}

campoPesquisa.addEventListener("keyup", (event) => {
    if (event.key == "Enter"){
        executarPesquisa();
    }else {
        obterSugestaoNomes(campoPesquisa.value.trim());
    }
});

campoPesquisa.addEventListener("focusin", (event) => {
    abrirSobreTela("caixaPesquisa")
});

function abrirCampoPesquisa(){
    console.log(barraPesquisa.classList)
    if (barraPesquisa.classList.contains("aberto")){
        fecharSobreTela("caixaPesquisa", true);
        fecharSobreTela("caixaFiltro", true);
        barraPesquisa.classList.remove("aberto");
    }else{
        barraPesquisa.classList.add("aberto");
        barraPesquisa.style.width = "calc("+ document.documentElement.clientWidth + "px - 70px)";

        const styles = getComputedStyle(caixaPesquisa);
        const duracao = styles.transitionDuration.split(',')[0].trim();
        const atraso = styles.transitionDelay.split(',')[0].trim();

        const toMs = (v) => v.endsWith('ms') ? parseFloat(v) : parseFloat(v) * 1000;
        const total = toMs(duracao) + toMs(atraso);

        if (total > 0) {
            setTimeout(() => campoPesquisa.focus(), total);
        }
    }
}

var btAbrirFiltrosFoco = false;
btnFiltrosAbrirFiltros.addEventListener("focusin", (event) => {
    btAbrirFiltrosFoco = true;
    abrirSobreTela("caixaFiltro");
});

btnFiltrosAbrirFiltros.addEventListener("click", (event) => {
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
        elementosMovimentarTeclado = [btnMenu, btnInicio, btnLivros, btnFeed, btnAjuda, btnUsuario, btnNotificacoes];
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
    console.log(document.activeElement.tagName != "INPUT" && document.activeElement.type != "text", document.activeElement.tagName != "INPUT", document.activeElement.type != "text")
    if (document.activeElement.tagName != "INPUT" || document.activeElement.type != "text"){
        if (event.key == "ArrowUp"){executarMovimentacaoTeclado("w");}
        else if (event.key == "ArrowDown"){executarMovimentacaoTeclado("s");}
        else if (event.key == "ArrowLeft"){executarMovimentacaoTeclado("a");}
        else if (event.key == "ArrowRight"){executarMovimentacaoTeclado("d");}
    }
    if (event.key === "Enter"){
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
    barraPesquisa.style.width = "calc("+ document.documentElement.clientWidth + "px - 70px)";
    atualizarTamanhoCaixaPesquisa();
    atualizarTamanhoCaixaFiltros();
});

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