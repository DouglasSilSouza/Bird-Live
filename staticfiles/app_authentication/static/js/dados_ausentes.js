
function enviardados(){
    const form = document.querySelector('#form-checkout'),
        nome = form.querySelector('#form-checkout__payerFirstName').value,
        sobrenome = form.querySelector('#form-checkout__payerLastName').value,
        birthday = form.querySelector('#form-birthday').value,
        email = form.querySelector('#form-checkout__email').value,
        typeDocument = form.querySelector('#type_document').value,
        cpf_cnpj = form.querySelector('#cpf_cnpj').value,
        codearea = form.querySelector('#codearea').value,
        phone = form.querySelector('#phone').value,
        formCep = form.querySelector('#form-cep').value,
        formEndereco = form.querySelector('#endereco').value,
        number = form.querySelector('#number').value,
        complemento = form.querySelector('#complemento').value;
        csrftoken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch ('/payments/verificar_dados_ausentes/',{
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken, // Inclui o csrf-token no cabeçalho
        },
        body: JSON.stringify({
            "nome": nome,
            "sobrenome": sobrenome,
            "birthday": birthday,
            "email": email,
            "type_document": typeDocument,
            "cpf_cnpj": cpf_cnpj,
            "codearea": codearea,
            "phone": phone,
            "formCep": formCep,
            "formEndereco": formEndereco,
            "number": number,
            "complemento": complemento
        })
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data.code === 200) {
            Swal.fire({
                icon: 'success',
                title: 'Dados enviados com Sucesso!',
                text: data.message,
                showConfirmButton: true,
                confirmButtonText: 'OK',
              }).then((result) => {
                if (result.isConfirmed) {
                  window.location.href = "/payments/payment/";
                }
              });
              
                
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Erro aos enviar os dados!',
                text: data.message,
                })
        }
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Erro ao processar os dados!',
            text: 'Erro: ' + error.message,
            })
    })
}

function validateField(input) {
    const label = document.querySelector(`label[for="${input.id}"]`);
    const labelName = label ? label.textContent : 'campo';
    let hasErrors = false;

    const removeErrorMessage = () => {
        if (input.nextElementSibling && input.nextElementSibling.classList.contains('text-helper')) {
            input.nextElementSibling.remove();
            input.classList.remove('error-data');
            input.classList.add('valid-data');
        }
    };

    function addErrorMessage(input, message) {
        // Remova mensagens de erro anteriores, se houver
        const previousErrorMessage = input.nextElementSibling;
        if (previousErrorMessage && previousErrorMessage.classList.contains('text-helper')) {
            previousErrorMessage.remove();
        }
    
        // Adicione a nova mensagem de erro
        input.classList.remove('valid-data');
        input.classList.add('error-data');
        const messageHTML = `<span class="text-helper">&#10071; ${message}</span>`;
        input.insertAdjacentHTML("afterend", messageHTML);
        hasErrors = true;
    }

    if (input.value.trim() === '') {
        addErrorMessage(input, `O campo ${labelName} não pode estar em branco!`);
    } else if (input.id === 'codearea' || input.id === 'form-cep' || input.id === 'phone' || input.id === 'number' || input.id === 'cpf_cnpj') {
        if (!/^\d*$/.test(input.value)) {
            input.value = input.value.replace(/\D/g, '');
            addErrorMessage(input, `O campo ${labelName} deve conter somente números!`);
        } else {
        removeErrorMessage();
        }

        if (input.id === 'phone') {
            // Validação do telefone
            input.addEventListener('blur', () => {
                removeErrorMessage();
                const phoneValue = input.value.replace(/\D/g, ''); // Remove não dígitos
    
                if (!/^\d{11}$/.test(phoneValue) && input.value.length < 11) {
                    addErrorMessage(input ,`O campo ${labelName} deve conter 11 dígitos numéricos!`);
                } else {
                    // Remova a formatação atual (se houver) antes de aplicar a máscara
                    input.value = phoneValue;
                    // Aplique a máscara apenas se a validação for bem-sucedida
                    $('#phone').mask('(00) 00000-0000');
                }
            });
        }

        if (input.id === 'form-cep') {
            // Validação do telefone
            input.addEventListener('blur', () => {
                removeErrorMessage();
                const phoneValue = input.value.replace(/\D/g, ''); // Remove não dígitos
    
                if (!/^\d{8}$/.test(phoneValue) && input.value.length < 8) {
                    addErrorMessage(input ,`O campo ${labelName} deve conter 8 dígitos numéricos!`);
                } else {
                    // Remova a formatação atual (se houver) antes de aplicar a máscara
                    input.value = phoneValue;
                    // Aplique a máscara apenas se a validação for bem-sucedida
                    $('#form-cep').mask('00000-000');
                }
            });
        }

        if (input.id === 'codearea') {
            // Validação do telefone
            input.addEventListener('blur', () => {
                removeErrorMessage();
                const phoneValue = input.value.replace(/\D/g, ''); // Remove não dígitos
    
                if (!/^\d{1}$/.test(phoneValue) && input.value.length < 1) {
                    addErrorMessage(input ,`O campo ${labelName} deve conter no mínimo 1 dígitos numéricos!`);
                } else {
                    // Remova a formatação atual (se houver) antes de aplicar a máscara
                    input.value = phoneValue;
                    // Aplique a máscara apenas se a validação for bem-sucedida
                    $('#codearea').mask('000');
                }
            });
        }
    } else if (input.id === 'type_document') {
        input.addEventListener('change', () => {
            const cpfCnpjInput = document.querySelector('#cpf_cnpj')

            if (input.value === 'cpf' || input.value === 'cnpj') {
                // Se for 'cpf' ou 'cnpj', ative o input
                cpfCnpjInput.removeAttribute('disabled');
            } else {
                // Caso contrário, desative o input
                cpfCnpjInput.setAttribute('disabled', 'disabled');
            }

            cpfCnpjInput.addEventListener('input', () => {

                if (input.value === 'cpf') {
                    // Validação do telefone
                    input.addEventListener('blur', () => {
                        removeErrorMessage();
                        const phoneValue = cpfCnpjInput.value.replace(/\D/g, ''); // Remove não dígitos
            
                        if (!/^\d{11}$/.test(phoneValue) && cpfCnpjInput.value.length < 11) {
                            addErrorMessage(cpfCnpjInput ,`O campo ${labelName} deve conter 11 dígitos numéricos!`);
                        } else {
                            // Remova a formatação atual (se houver) antes de aplicar a máscara
                            cpfCnpjInput.value = phoneValue;
                            // Aplique a máscara apenas se a validação for bem-sucedida
                            removeErrorMessage();
                            $('#cpf_cnpj').mask('000.000.000-00');
                        }
                    });
                } else if (input.value === 'cnpj') {
                    // Validação do telefone
                    input.addEventListener('blur', () => {
                        removeErrorMessage();
                        const phoneValue = cpfCnpjInput.value.replace(/\D/g, ''); // Remove não dígitos
            
                        if (!/^\d{14}$/.test(phoneValue) && cpfCnpjInput.value.length < 14) {
                            addErrorMessage(cpfCnpjInput ,`O campo ${labelName} deve conter 14 dígitos numéricos!`);
                        } else {
                            // Remova a formatação atual (se houver) antes de aplicar a máscara
                            cpfCnpjInput.value = phoneValue;
                            // Aplique a máscara apenas se a validação for bem-sucedida
                            removeErrorMessage();
                            $('#cpf_cnpj').mask('00.000.000/0000-00');
                        }
                    });
                }
            })
            
        });
    } else {
        removeErrorMessage();
    }

    return hasErrors
}

function searchCep (cep) {
    return fetch (`https://brasilapi.com.br/api/cep/v2/${cep}`)
    .then(response => {
        if (!response.ok) {
          throw new Error(`Erro na requisição: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.errors) {
            throw new Error('CEP inválido ou não encontrado');
        } else {
            return data; // Retorna os dados do CEP
        }
    });
}

const inputCep = document.querySelector('#form-cep');
inputCep.addEventListener('input', () => {
    const bairro = document.querySelector('#form-bairro');
    const rua = document.querySelector('#endereco');
    const numericCount = (inputCep.value.match(/\d/g) || []).length; // Conta a quantidade de números
    if (numericCount === 8) {
        showLoadingModal(); // Mostra a tela de carregamento
        searchCep(inputCep.value) // Pega os dados com Fecth
        .then(data => {
            // Fecha a tela de carregamento
            Swal.close();
            // Atualiza os campos de rua e bairro
            rua.value = data.street; // Preenche o campo de rua com a informação da API
            bairro.value = data.neighborhood; // Preenche o campo de bairro com a informação da API

            // Remove a mensagem de erro quando o campo não estiver vazio
            if (inputCep.value.trim() !== '') {
                removeErrorForField(rua);
                removeErrorForField(bairro);
            }
        })
        .catch(error => {
            // Fecha a tela de carregamento em caso de erro
            console.error(error)
            Swal.close();
            Swal.fire({
                icon: 'error',
                title: 'Erro na consulta do CEP',
                text: error,
            })
        });
    } //else {
    //     ruaInput.value = ''; // Limpa o campo de rua se o CEP for inválido
    //     bairroInput.value = ''; // Limpa o campo de bairro se o CEP for inválido
    // }
})

function showLoadingModal() {
    Swal.fire({
        title: 'Carregando...',
        allowOutsideClick: false,
        allowEnterKey: false,
        showConfirmButton: false,
        onBeforeOpen: () => {
            Swal.showLoading();
        }
    });
}

// Função para remover a mensagem de erro de um campo
function removeErrorForField(input) {
    const errorMessages = document.querySelectorAll(`label[for="${input.id}"] .text-helper`);
    if (input.classList.contains('error-data')) {
        input.classList.remove('error-data')
        input.classList.add('valid-data');
    }    
    errorMessages.forEach(message => message.remove());
}

function validationForm() {
    const form = document.querySelector('#form-checkout'),
        requireds = form.querySelectorAll('.required');

    // Adicione manipuladores de eventos para validação em tempo real
    requireds.forEach(required => {
        required.addEventListener('input', () => {
            validateField(required)
        });
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        let hasErrors = false;

        // Verifica campos vazios e exibe mensagens de erro
        requireds.forEach(required => {
            
            if (validateField(required)) {
                validateField(required);
                hasErrors = validateField(required);
            } else {
                removeErrorForField(required);
            }
        });
        if (!hasErrors) {
            enviardados();
        }
    });
}

validationForm();
