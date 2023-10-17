const nome = document.getElementById('nome')
const sobrenome = document.getElementById('sobrenome')
const email = document.getElementById('email')
const password = document.getElementById('password')
const conf_password = document.getElementById('conf_password')

const form = document.getElementById('form')
const paragrafos = document.getElementById('warning')

form.addEventListener("submit", e=> {
    let warning = ""
    let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
    let regexSenha = /^(?=.*[A-Z])(?=.*[!#@$%&])(?=.*[0-9])(?=.*[a-z]).{6,15}$/
    let entrar = false

    if (nome.value.length <= 3){
        warning += "Digite um nome válido! <br>"
        nome.style.borderColor = 'red';
        nome.style.boxShadow = '0 10px 10px red';
        nome.style.display = 'block';
        entrar = true
    }

    if (sobrenome.value.length <= 3){
        warning += "Digite um sobrenome válido! <br>"
        sobrenome.style.borderColor = 'red';
        sobrenome.style.boxShadow = '0 10px 10px red'
        sobrenome.style.display = 'block';
        entrar = true
    }

    if (email.value.length == 0){
        warning += "Digite o campo 'E-mail'! <br>"
        email.style.borderColor = 'red'
        email.style.boxShadow = '0 10px 10px red'
        email.style.display = 'block';
        entrar = true
    }

    if (password.value.length == 0){
        warning += "Digite o campo 'Senha'! <br>"
        password.style.borderColor = 'red'
        password.style.boxShadow = '0 10px 10px red'
        password.style.display = 'block';
        entrar = true
    }

    if (conf_password.value.length == 0){
        warning += "Digite o campo de 'Confirmação de senha'! <br>"
        conf_password.style.borderColor = 'red'
        conf_password.style.boxShadow = '0 10px 10px red'
        conf_password.style.display = 'block';
        entrar = true
    }
    
    if (!regexEmail.test(email.value)) {
        warning += "E-mail inválido! <br>"
        email.style.borderColor = 'red'
        email.style.boxShadow = '0 10px 10px red'
        email.style.display = 'block';
        entrar = true
    }

    if (password.value.length <= 7) {
        warning += "Digite uma senha maior que 8 caracteres! <br>"
        password.style.borderColor = 'red'
        password.style.boxShadow = '0 10px 10px red'
        password.style.display = 'block';
        entrar = true
    }

    if (!regexSenha.test(password.value)){
        warning += "Senha deve possui pelos menos uma letra maiúscula, minúscula e caracte especial! (!#@$%&) <br>"
        password.style.borderColor = 'red'
        password.style.boxShadow = '0 10px 10px red'
        password.style.display = 'block';
        entrar = true
    }
    
    if (password.value !== conf_password.value) {
        warning += "Senhas não são iguais! <br>"
        password.style.borderColor = 'red'
        password.style.boxShadow = '0 10px 10px red'
        password.style.display = 'block';
        conf_password.style.borderColor = 'red'
        conf_password.style.boxShadow = '0 10px 10px red'
        conf_password.style.display = 'block';
        entrar = true
    }

    if (entrar) {
        let warningHTML = '<strong>'
        const messages = warning.split("<br>").filter(message => message.trim() !== "");
        if (messages.length > 0) {
            messages.forEach((message) => {
                warningHTML += '<i class="bi bi-exclamation-circle-fill"></i>' + message.trim() + '<br>'
            });
            warningHTML += '</strong>'
            paragrafos.innerHTML = warningHTML;
            paragrafos.style.display = 'block';
            e.preventDefault()
        } else {
            paragrafos.innerHTML = "";
            paragrafos.style.display = 'none';
        }
    }
})