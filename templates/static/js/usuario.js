var interacoesPerfil = document.getElementById('interacoesPerfil');
var interacoesPerfilVisualizacao = document.getElementById('interacoesPerfilVisualizacao');
var areaListasUsuario = document.getElementById('areaListasUsuario');

Array.prototype.forEach.call(interacoesPerfil.getElementsByTagName('button'), function(btn){
    btn.addEventListener('click', function(event){
        btn_aux = interacoesPerfil.querySelector('.selecionado').classList.remove("selecionado");
        btn.classList.add('selecionado');
        
        interacoesPerfilVisualizacao.querySelector('.selecionado').classList.remove('selecionado');
        interacoesPerfilVisualizacao.querySelector('#' + btn.id + 'Conteudo').classList.add('selecionado');
    })
});

var btnSeguirUsuario = document.getElementById('btnSeguirUsuario');
var btnDeixarSeguirUsuario = document.getElementById('btnDeixarSeguirUsuario');
if (btnSeguirUsuario){
    btnSeguirUsuario.addEventListener('click', function(event){
        var idUsuario = document.getElementById('idUsuario').innerText;

        fetch('/seguirUsuario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idUsuarioSeguir: idUsuario})
        })
        .then(response => response.json())
        .then(retorno => {
            
        }).catch(error => { console.error('Erro:', error); });
    });
}

if (btnDeixarSeguirUsuario){
    btnDeixarSeguirUsuario.addEventListener('click', function(event){
        var idUsuario = document.getElementById('idUsuario').innerText;

        fetch('/deixarSeguirUsuario', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({idUsuarioDeixarSeguir: idUsuario})
        })
        .then(response => response.json())
        .then(retorno => {
            
        }).catch(error => { console.error('Erro:', error); });
    });
}

retornarListas();
