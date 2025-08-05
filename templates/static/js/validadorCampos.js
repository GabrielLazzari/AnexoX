
$(document).ready(function(){
    $('#campoCnpj').mask('00.000.000/0000-00');
});

Array.prototype.forEach.call(document.getElementsByTagName('form'), function(form){
    form.querySelector('button[type="submit"]').addEventListener('click', function(event) {
        event.preventDefault();
        var podeEnviarForm = true;
        Array.prototype.forEach.call(form.getElementsByTagName('input'), function(input){
            if (input.getAttribute("required") != null && input.value.trim() == ""){
                adicinoarEdicaoCampoObrigatorio(input);
                podeEnviarForm = false;
            }
        });
        
        if (podeEnviarForm){
            form.submit();
        }
    });
})

function adicinoarEdicaoCampoObrigatorio(input){
    input.classList.add("inputMsgErro");
    if (input.nextElementSibling == null || !input.nextElementSibling.classList.contains("spanMsgErro")){
        input.insertAdjacentHTML('afterend', '<span class="spanMsgErro">Campo obrigatório</span>');
    }
    input.addEventListener("input", detectarEdicaoCampoObrigatorio);
}

function detectarEdicaoCampoObrigatorio(){
    this.removeEventListener('input', detectarEdicaoCampoObrigatorio);
    if (this.nextElementSibling.classList.contains("spanMsgErro")){
        this.nextElementSibling.remove();
    }
    this.classList.remove("inputMsgErro");
}

var style = document.createElement('style');
style.textContent = `
    .spanMsgErro{
        color: red;
        font-size:12px;
    }

    .inputMsgErro{
        border-color: red;
    }
    
    .msgRetornoErro{
        color: red;
    }
`;
document.head.appendChild(style);