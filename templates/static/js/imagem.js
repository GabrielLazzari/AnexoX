
function dragOverHandler(ev) {
    ev.preventDefault();
}

function dropHandler(event) {
    event.preventDefault();

    if (event.dataTransfer.items.length > 0 && event.dataTransfer.items[0].kind === 'file') {
        const file = event.dataTransfer.items[0].getAsFile();
        carregarImagem(null, file)
    }
}


function carregarImagem(input=null, valor=null){
    if (input == null){
        input = document.querySelector('input[type="file"]');
        if (input == null){
            return;
        }
    }

    var reader = new FileReader();
    
    reader.onload = function () {
        if (reader.result.startsWith('data:image/') || reader.result.startsWith('image/')){
            var imagem = new Image();      
            imagem.src = reader.result;

            imagem.onload = function(){
                console.log('tamOrg', this.width + ',' + this.height);
                input.parentElement.style.backgroundImage = `url(${reader.result})`;
            }
        }
    }

    if (valor == null){
        valor = input.files[0]
    }

    reader.readAsDataURL(valor);
}

function CarregarImagemCapaPerfil(input=null, valor=null){
    if (input == null){
        input = document.querySelector('input[type="file"]');
        if (input == null){
            return;
        }
    }

    var reader = new FileReader();
    
    reader.onload = function () {
        if (reader.result.startsWith('data:image/') || reader.result.startsWith('image/')){
            var imagem = new Image();      
            imagem.src = reader.result;

            imagem.onload = function(){
                //console.log('tamOrg', this.width + ',' + this.height);
                //input.parentElement.style.backgroundImage = `url(${reader.result})`;
                fetch('/alterarImagemCapaUsuario', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        imagem: reader.result
                    })
                })
                .then(response => response.json())
                .then(retorno => {
                    if (retorno.erro != ""){
                        toast.erro(retorno.erro);
                    }else{
                        var imagemCapaPerfil = document.getElementById("imagemCapaPerfil");
                        console.log(retorno)
                        if (imagemCapaPerfil){
                            //imagemCapaPerfil.src = retorno.imagem;
                            retornarImagemCapaUsuario(document.getElementById('idUsuario').innerText);
                        }
                    }
                }).catch(error => { console.error('Erro:', error); });
            }
        }
    }

    if (valor == null){
        valor = input.files[0]
    }

    reader.readAsDataURL(valor);
}

function retornarImagemCapaUsuario(idUsuario){
    fetch('/retornarImagemCapaUsuario', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ idUsuario: idUsuario })
    })
    .then(response => response.json())
    .then(retorno => {
        if (retorno.erro != ""){
            toast.erro(retorno.erro);
        }else{
            var imagemCapaPerfil = document.getElementById("imagemCapaPerfil");
            if (imagemCapaPerfil){
                imagemCapaPerfil.src = retorno.imagem
            }
        }
    }).catch(error => { console.error('Erro:', error); });
}
