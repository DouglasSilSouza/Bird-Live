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

function enviarDados() {
    
    const button = document.querySelector('#add-cart'),
        CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value,
        idProduct = document.querySelector('#idproduct').value;
    
    button.addEventListener('click', () => {
        let qtd = qtdText.textContent;
        // Configuração da requisição
        const options = {
            method: "POST", // Método HTTP que você deseja usar (neste caso, POST)
            headers: {
            "Content-Type": "application/json", // Tipo de conteúdo sendo enviado (JSON neste exemplo)
            "X-CSRFToken": CSRFToken,
            },
            body: JSON.stringify({"qtd": qtd, "idProduct": idProduct}), // Converte os dados para JSON e os coloca no corpo da requisição
        };
        fetch('/products/getdatacart/', options)
        .then(response => {
            if (!response.ok) {
              throw new Error(`Erro na requisição: ${response.status}`);
            }
            return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
          })
          .then(data => {
            console.log("Resposta da API:", data);
            // Faça algo com os dados da resposta, se necessário
          })
          .catch(error => {
            console.error("Erro:", error);
          });
    })
}
quantidade()
enviarDados()