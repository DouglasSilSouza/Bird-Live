// Função que faz a solicitação AJAX
function obterChavePublica() {
  return new Promise(function (resolve, reject) {
    fetch("/payments/endpoints_api/", {
      method: "get",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Erro na requisição: ${response.status}`);
        }
        return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
      })
      .then((data) => {
        var publicKey = data.public_key;
        resolve(publicKey); // Resolve a promessa com a chave pública
      })
      .catch((error) => {
        reject("Erro ao obter a chave pública."); // Rejeita a promessa em caso de erro
      });
  });
}

let notification = [];
// Função assíncrona para carregar o MercadoPago e criar o objeto
export async function inicializarMercadoPago() {
  return new Promise(async (resolve, reject) => {
    try {
      const publicKey = await obterChavePublica();
      const mp = new window.MercadoPago(publicKey);
      const valor = document.querySelector("#valortotal");

      let valorformat = valor.value.replace(",", ".")

      const cardForm = mp.cardForm({
        amount: valorformat,
        iframe: true,
        form: {
          id: "form-checkout",
          cardNumber: {
            id: "form-checkout__cardNumber",
            placeholder: "Número do cartão",
          },
          expirationMonth: {
            id: "form-checkout__expirationMonth",
            placeholder: "MM",
          },
          expirationYear: {
            id: "form-checkout__expirationYear",
            placeholder: "YY",
          },
          securityCode: {
            id: "form-checkout__securityCode",
            placeholder: "Código de segurança",
          },
          cardholderName: {
            id: "form-checkout__cardholderName",
            placeholder: "Titular do cartão",
          },
          issuer: {
            id: "form-checkout__issuer",
            placeholder: "Banco emissor",
          },
          installments: {
            id: "form-checkout__installments",
            placeholder: "Parcelas",
          },
          identificationType: {
            id: "form-checkout__identificationType",
            placeholder: "Tipo de documento",
          },
          identificationNumber: {
            id: "form-checkout__identificationNumber",
            placeholder: "Número do documento",
          },
          cardholderEmail: {
            id: "form-checkout__cardholderEmail",
            placeholder: "E-mail",
          },
        },
        callbacks: {
          onFormMounted: (error) => {
            if (error)
              return console.warn("Form Mounted handling error: ", error);
          },
          onSubmit: (event) => {
            event.preventDefault();

            const {
              paymentMethodId: payment_method_id,
              issuerId: issuer_id,
              cardholderEmail: email,
              amount,
              token,
              installments,
              identificationNumber,
              identificationType,
            } = cardForm.getCardFormData();

            const CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;

            const options = {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRFToken,
              },
              body: JSON.stringify({
                token,
                issuer_id,
                payment_method_id,
                transaction_amount: Number(amount),
                installments: Number(installments),
                description: "Descrição do produto",
                payer: {
                  email,
                  identification: {
                    type: identificationType,
                    number: identificationNumber,
                  },
                },
              }),
            }

            fetch("/payments/process_payment_card/")
            .then((response) => {
              if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
              }
              return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
            })
            .then((data) => {
              if (data.code == 200) {
                Swal.showLoading();
                Swal.fire({
                  icon: "info",
                  title: "Pagamento feito",
                });
              } else {
                Toast.fire({
                  icon: "error",
                  title: `${data.message} | Status: ${data.code}`,
                });
              }
            })
            .catch((error) => {
              Toast.fire({
                icon: "error",
                title: "Erro ao enviar dados" + error,
              });
            });
          },
        },
      });
      resolve();
    } catch (error) {
      reject(error);
    }
  });
}

// Chame a função assíncrona para iniciar o processo
// inicializarMercadoPago()
// .then(() => {

//   let iframe = document.querySelector('#form-checkout__securityCode iframe');
//   // let iframe = form_securityCode.querySelector('iframe')

//   iframe.onload = function () {
//     // Acessar o documento interno do iframe
//     var iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

//     // Agora você pode acessar os elementos e atributos dentro do documento interno do iframe
//     var elemento = iframeDocument.getElementById('idDoElementoNoIframe');
//     var valorDoAtributo = elemento.getAttribute('nomeDoAtributo');

//     // Faça algo com o elemento ou atributo
//     console.log("Valor do atributo: " + valorDoAtributo);
// };

//   document.querySelector('.card-number-input').oninput = () =>{
//     document.querySelector('.card-number-box').innerText = document.querySelector('.card-number-input').value;
//   }

//   document.querySelector('.card-holder-input').oninput = () =>{
//     document.querySelector('.card-holder-name').innerText = document.querySelector('.card-holder-input').value;
//   }

//   document.querySelector('.month-input').oninput = () =>{
//     document.querySelector('.exp-month').innerText = document.querySelector('.month-input').value;
//   }

//   document.querySelector('.year-input').oninput = () =>{
//     document.querySelector('.exp-year').innerText = document.querySelector('.year-input').value;
//   }

//   document.querySelector('.cvv-input').onmouseenter = () =>{
//     document.querySelector('.front').style.transform = 'perspective(1000px) rotateY(-180deg)';
//     document.querySelector('.back').style.transform = 'perspective(1000px) rotateY(0deg)';
//   }

//   document.querySelector('.cvv-input').onmouseleave = () =>{
//     document.querySelector('.front').style.transform = 'perspective(1000px) rotateY(0deg)';
//     document.querySelector('.back').style.transform = 'perspective(1000px) rotateY(180deg)';
//   }

//   document.querySelector('.cvv-input').oninput = () =>{
//     document.querySelector('.cvv-box').innerText = document.querySelector('.cvv-input').value;
//   }
// })
// .catch(error => {
//   console.error(error);
// });
