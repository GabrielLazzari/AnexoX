var interacoesPerfil = document.getElementById('interacoesPerfil');
var interacoesPerfilVisualizacao = document.getElementById('interacoesPerfilVisualizacao');
var areaListasUsuario = document.getElementById('areaListasUsuario');

Array.prototype.forEach.call(interacoesPerfil.getElementsByTagName('button'), function(btn){
    btn.addEventListener('click', function(event){
        btn_aux = interacoesPerfil.querySelector('.selecionado')
        if (btn_aux.id == btn.id) return;
        btn_aux.classList.remove("selecionado");
        btn.classList.add('selecionado');
        
        interacoesPerfilVisualizacao.querySelector(':scope > .selecionado').classList.remove('selecionado');
        interacoesPerfilVisualizacao.querySelector('#' + btn.id + 'Conteudo').classList.add('selecionado');
        if (btn.id == "interacaoPerfilLivros"){
            retornarListas();

        }else if (btn.id == "interacaoPerfilSeguindo"){
            retornarUsuariosSeguir("seguindo");

        }else if (btn.id == "interacaoPerfilSeguidores"){
            retornarUsuariosSeguir("seguidores");

        }else if (btn.id == "interacaoPerfilPublicacoes"){
            console.log("publicacaoes");
        }
    })
});

var btnSeguirUsuario = document.getElementById('btnSeguirUsuario');
if (btnSeguirUsuario){
    btnSeguirUsuario.addEventListener('click', function(event){
        var idUsuario = document.getElementById('idUsuario').innerText;

        fetch('/controleSeguirUsuario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idUsuarioSeguir: idUsuario})
        })
        .then(response => response.json())
        .then(retorno => {
            if (retorno.erro != "") {
                toast.erro(retorno.erro);
            }else{
                if (retorno.seguindo){
                    btnSeguirUsuario.innerText = "Deixar de Seguir";
                }else{
                    btnSeguirUsuario.innerText = "Seguir";
                }
            }
        }).catch(error => { console.error('Erro:', error); });
    });
}

function retornarUsuariosSeguir(tipo="seguindo"){
    if (tipo == "seguindo"){
        tipo = '/retornarUsuariosSeguindo';
    }else{
        tipo = '/retornarUsuariosSeguidores';
    }

    var idUsuario = document.getElementById('idUsuario').innerText;

    fetch(tipo, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idUsuario: idUsuario})
    })
    .then(response => response.json())
    .then(retorno => {
        console.log(retorno);
        if (retorno.erro != "") {
            toast.erro(retorno.erro);
        }else{
            if (tipo == '/retornarUsuariosSeguindo'){
                carregarUsuarioSeguir(retorno.usuarios, document.getElementById('interacaoPerfilSeguindoConteudo'))
            }else{
                carregarUsuarioSeguir(retorno.usuarios, document.getElementById('interacaoPerfilSeguidoresConteudo'))
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}

function carregarUsuarioSeguir(usuarios, el){
    el.innerHTML = "";
    for (var usuario of usuarios){
        console.log(conteudoHtmlUsuario(usuario))
        el.innerHTML += conteudoHtmlUsuario(usuario);
    }
}

retornarListas();
