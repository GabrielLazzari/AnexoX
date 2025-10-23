var elqtdNotificacoes = document.getElementById('qtdNotificacoes');
var conteudoNotificacoes = document.getElementById('conteudoNotificacoes');

function mudarCorIconeNotificacao(temNotificacao=false){
    Array.prototype.forEach.call(document.getElementsByName('acessarNotificacoes'), function(nt){
        if (temNotificacao){
            nt.querySelector('img').style.filter = "brightness(0) saturate(100%) invert(11%) sepia(98%) saturate(5984%) hue-rotate(0deg) brightness(102%) contrast(103%)";
        }else{
            nt.querySelector('img').style.filter = "unset";
        }
    });
}

function conteudoHtmlNotificacao(notificacao){
    var href = "";
    var tag = "div";
    if (notificacao.link != ""){
        href = `href="${notificacao.link}"`
        tag = "a"
    }
    return `
        <div class="itemNotificacao" idNotificacao="${notificacao.id}">
            <img src="${notificacao.img}" alt="">
            <div>
                <div class="tituloItemNotificacao">${notificacao.titulo}<button class="descartarNotificacao" onclick="removerNotificacao(this)">x</button></div>
                <${tag} ${href} class="conteudoItemNotificacao">${notificacao.conteudo}</${tag}>
            </div>
        </div>
    `;
}

function atualizarNotificacoes(){
    fetch('/procurarNotificacoes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro){
            conteudoNotificacoes.innerHTML = retorno.erro;
        }else{
            if (retorno.notificacoes.length > 0){
                conteudoNotificacoes.innerHTML = "";
                mudarCorIconeNotificacao(true);
            }else{
                conteudoNotificacoes.innerHTML = "Nenhuma nova notificação";
                mudarCorIconeNotificacao(false);
            }
            
            elqtdNotificacoes.innerHTML = `(${retorno.notificacoes.length})`

            for (var notificacao of retorno.notificacoes){
                conteudoNotificacoes.innerHTML += conteudoHtmlNotificacao(notificacao);
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

function removerNotificacao(btn){
    var nt = btn.closest(".itemNotificacao");

    fetch('/removerNotificacao', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idNotificacao: nt.getAttribute("idNotificacao")})
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro){
            toast.erro(retorno.erro);
        }else{
            if (retorno.qtdNotificacoes > 0){
                mudarCorIconeNotificacao(true);
            }else{
                conteudoNotificacoes.innerHTML = "Nenhuma nova notificação";
                mudarCorIconeNotificacao(false);
            }

            elqtdNotificacoes.innerHTML = `(${retorno.qtdNotificacoes})`

            nt.remove();
        }
    }).catch(error => { console.error('Erro:', error); });
}

atualizarNotificacoes();
