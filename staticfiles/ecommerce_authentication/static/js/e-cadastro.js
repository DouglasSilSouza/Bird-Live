// Função para verificar o formato do e-mail usando expressão regular em JavaScript
function isValidEmail(email) {
    var regexEmail = /([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])/;
    return regexEmail.test(email);
}

// Função para verificar a senha em JavaScript
function isValidPassword(password) {
    var regexPassword = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    return regexPassword.test(password);
}

// Função para realizar as verificações do formulário no lado do cliente
function validateForm() {
    const form = document.getElementsByTagName("form")
    var nome = document.getElementById('nome').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('senha').value;
    var confPassword = document.getElementById('conf_senha').value;

    form.

    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type !== 'submit' && inputs[i].value.trim() === '') {
            alert("Por favor, preencha todos os campos.");
            return false;
        }
    }

    if (password !== confPassword) {
        alert("Senhas não coincidem!");
        return false;
    }

    if (!isValidEmail(email)) {
        alert("E-mail inválido!");
        return false;
    }

    if (!isValidPassword(password)) {
        alert("Senha inválida! Deve conter uma letra maiúscula, minúscula, número e caractere especial.");
        return false;
    }

    if (nome.length <= 3) {
        alert("Nome inválido!");
        return false;
    }


    return true;
}