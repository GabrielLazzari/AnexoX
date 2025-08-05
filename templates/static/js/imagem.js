
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
