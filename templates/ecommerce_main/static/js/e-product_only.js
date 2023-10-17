function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function parcelas() {
    const tabela = document.querySelector('#parcelas');
    const valor = document.querySelector('#valor');

    let formatValor = parseFloat(valor.textContent.replace('R$', '').replace(',', '.').trim()); // Substituímos ',' por '.' para fazer o parse corretamente
    let parcelas = 1;

    if (formatValor <= 100.00) {
        parcelas = 2;
    } else if (formatValor <= 150.00) {
        parcelas = 3;
    } else if (formatValor <= 200.00) {
        parcelas = 4;
    } else {
        parcelas = Math.min(Math.floor(formatValor / 50), 12);
    }

    const tabelaBody = tabela.querySelector('tbody');
    tabelaBody.innerHTML = '';

    for (let i = 1; i <= parcelas; i++) {
        let row = document.createElement('tr');
        let cell1 = document.createElement('td');
        let cell2 = document.createElement('td');

        cell1.textContent = i + ' S/ juros';
        cell2.textContent = formatCurrency(formatValor / i);

        row.appendChild(cell1);
        row.appendChild(cell2);
        tabelaBody.appendChild(row);
    }
}

const qtdText = document.querySelector('.qtd-text');

function quantidade() {
    const plus = document.querySelector('.plus');
    const dash = document.querySelector('.dash');

    // Declare uma variável global para armazenar o valor de qtd
    let qtd = 1;

    plus.addEventListener('click', () => {
        qtd++;
        qtdText.textContent = qtd;
    });

    dash.addEventListener('click', () => {
        if (qtd > 1) {
            qtd--;
            qtdText.textContent = qtd;
        }
    });
}

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener('mouseenter', Swal.stopTimer)
      toast.addEventListener('mouseleave', Swal.resumeTimer)
    }
  })

function enviarDados() {
    
    const button = document.querySelector('#add-cart'),
        CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value,
        idProduct = document.querySelector('#idproduct').value;
    
    button.addEventListener('click', () => {
        // Configuração da requisição

        const badge = document.querySelector("#badge");

        if( badge ) {
            if (badge.textContent === "") {
                badge.textContent = 1
            } else {
                let valorAtual = parseInt(badge.textContent);
                let soma = valorAtual + 1;
                badge.textContent = soma;
            }
        }

        const options = {
            method: "POST", // Método HTTP que você deseja usar (neste caso, POST)
            headers: {
            "Content-Type": "application/json", // Tipo de conteúdo sendo enviado (JSON neste exemplo)
            "X-CSRFToken": CSRFToken,
            },
            body: JSON.stringify({"qtd": 1, "idProduct": idProduct}), // Converte os dados para JSON e os coloca no corpo da requisição
        };
        fetch('/cart/getcart', options)
        .then(response => {
            if (!response.ok) {
              throw new Error(
                Toast.fire({
                    icon: 'error',
                    title: `Erro na requisição: ${response.status}`
                })
                );
            }
            return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
          })
          .then(data => {
          })
          .catch(error => {
            console.error(Toast.fire({
                icon: 'error',
                title: 'Error: ' +error.message
              }));
          });
    })
}
enviarDados()
parcelas();
