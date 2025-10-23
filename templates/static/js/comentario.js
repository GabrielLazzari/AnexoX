
var idComentarioAux = 0;

function comentar(obj, conteudo, telaOrigem, itemOrigemId, spoiler=false, comentarioPaiId=0){
    fetch('/gravarComentario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            conteudo: conteudo, 
            telaOrigem: telaOrigem, 
            itemOrigemId: itemOrigemId, 
            comentarioPaiId: comentarioPaiId,
            spoiler: spoiler
        })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro){
            toast.erro(retorno.erro);
        }else{
            adicionarComentario(obj, retorno.comentario, comentarioPaiId);
        }
    }).catch(error => { console.error('Erro:', error); });
}

function adicionarComentario(obj, comentario, comentarioPaiId) {
    var comentariosLista = null;
    if (comentarioPaiId != 0){
        var comentarioObj = document.querySelector("[idcomentario='" + comentarioPaiId + "']").closest(".comentario");
        comentariosLista = comentarioObj.querySelector(".respostas");
    }else{
        comentariosLista = obj.querySelector(".paginacaoItens");
    }

    if (obj){
        var msgTela = obj.querySelector(".msgTela");
        if (msgTela){
            msgTela.remove();
        }
    }
    
    if (!comentariosLista) return;
    
    novoComentarioHTML = conteudoHtmlComentario(comentario)[0];
    
    comentariosLista.insertAdjacentHTML('beforeend', novoComentarioHTML);
}

function reagirComentario(btn){
    btn.classList.toggle("reagido");

    var comentario = btn.closest(".comentario");
    var idComentario = comentario.querySelector("[idcomentario]").getAttribute("idcomentario");

    fetch('/reagirComentario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            idComentario: idComentario,
            reagido: btn.classList.contains("reagido")
        })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro){
            toast.erro(retorno.erro);
        }else{
            
        }
    }).catch(error => { console.error('Erro:', error); });
}

function abrirResponderComentario(btn, telaOrigemId, telaOrigem){
    comentario = btn.closest(".comentario:not(.comentarioResposta)");
    comentarioTab = comentario.querySelector(".respostas");

    var idComentario = comentario.querySelector("[idcomentario]").getAttribute("idcomentario");
    var imgUsuarioResponder = document.getElementById("imgUsuarioResponder").src;
    var comentarioResposta = document.createElement("div");
    comentarioResposta.classList = "comentario comentarioResposta";
    comentarioResposta.innerHTML = `
        <div class="comentario-form">
            <input type="hidden" idComentarioPai="${idComentario}">
            <img src="${imgUsuarioResponder}">
            <div class="comentario-input">
                <div style="display: flex;"><input type="checkbox" class="checkCotemSpoiler"> Contém Spoiler</div>
                <input type="text" class="input-comentario">
                <div class="comentario-acoes-form">
                    <button class="btn-enviar-comentario">Enviar</button>
                    <button class="btn-cancelar-comentario" onclick="this.closest('.comentario').remove();">Cancelar</button>
                </div>
            </div>
        </div>
    `;

    comentarioTab.insertAdjacentElement("beforeend", comentarioResposta);
    comentarioResposta.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
    inputComentario = comentarioResposta.querySelector(".input-comentario");
    inputComentario.focus();
    var btnEnviar = comentarioResposta.querySelector(".btn-enviar-comentario")
    btnEnviar.addEventListener("click", function(){
        var comentarioAux = this.closest(".comentario");
        if (!comentarioAux){
            return;
        }
        const textoComentario = comentarioAux.querySelector(".input-comentario").value.trim();
        if (textoComentario) {
            var idComentarioPai = 0;
            var elResponder = comentarioAux.querySelector("[idcomentariopai]");

            if (elResponder){
                idComentarioPai = elResponder.getAttribute("idcomentariopai");
            }
            
            if (idComentarioPai == 0){
                toast.erro("O comentário para ser respondido foi alterado ou não existe mais.")
            }else{
                var spoiler = comentarioResposta.querySelector(".checkCotemSpoiler").checked;
                comentar(null, textoComentario, telaOrigem, telaOrigemId, spoiler, idComentarioPai)
                
                comentarioAux.remove();
            }
        }
    })

    inputComentario.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (btnEnviar) {
                btnEnviar.click();
            }
        }
    });
}

function abrirInfoComentario(btn){
    var comentario = btn.closest(".comentario");
    var idComentario = comentario.querySelector("[idcomentario]").getAttribute("idcomentario");
    idComentarioAux = idComentario;
    abrirSobreTela('sobretelaInfoComentario', btn);
}

function excluirComentario(telaOrigem){
    if (!telaOrigem){
        return;
    }

    if (idComentarioAux == 0){
        toast.erro("Selecione um comentário escrito por você para excluir");
        return;
    }

    if (!window.confirm(`Deseja realmente remover o comentário?`)){
        return;
    }

    fecharSobreTela('sobretelaInfoComentario', true);

    fetch('/excluirComentario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            idComentario: idComentarioAux,
            origem: telaOrigem
        })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro){
            toast.erro(retorno.erro);
        }else{
            document.querySelector("[idcomentario='" + idComentarioAux + "']").closest(".comentario").remove();
            toast.sucesso("Comentário removido com sucesso!");
        }
    }).catch(error => { console.error('Erro:', error); });
}