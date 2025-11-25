
$(document).ready(function(){
    $('#campoCnpj').mask('00.000.000/0000-00');
});

Array.prototype.forEach.call(document.getElementsByTagName('form'), function(form){
    var btn = form.querySelector('button[type="submit"]')
    criarEventoCampoObrigatorio(btn);
})

const validarEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

function criarEventoCampoObrigatorio(btn, enviarForm=true){
    if (!btn) return;
    
    var form = btn.closest("form");

    if (!form) return;

    btn.addEventListener('click', function(event) {
        event.preventDefault();
        var podeEnviarForm = true;
        Array.prototype.forEach.call(form.getElementsByTagName('input'), function(input){
            if (input.getAttribute("required") != null && input.value.trim() == ""){
                adicinoarEdicaoCampoObrigatorio(input);
                podeEnviarForm = false;

            }else if (input.getAttribute("email") != null && !validarEmail(input.value.trim())){
                adicinoarEdicaoCampoObrigatorio(input, "E-mail inválido");
                podeEnviarForm = false;
            }
        });
        
        if (podeEnviarForm && enviarForm){
            form.submit();
        }
    });
}

function adicinoarEdicaoCampoObrigatorio(input, msg="Campo obrigatório"){
    input.classList.add("inputMsgErro");
    if (input.nextElementSibling == null || !input.nextElementSibling.classList.contains("spanMsgErro")){
        input.insertAdjacentHTML('afterend', `<span class="spanMsgErro">${msg}</span>`);
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