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
          let publicKey = data.public_key,
              total = data.total,
              infoProdutos = data.infoProdutos;
          resolve({publicKey, total, infoProdutos}); // Resolve a promessa com a chave pública
        })
        .catch((error) => {
          reject("Erro ao obter a chave pública."); // Rejeita a promessa em caso de erro
        });
    });
  }

const CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;

let notification = [];
// Função assíncrona para carregar o MercadoPago e criar o objeto
async function inicializarMercadoPago() {
  return new Promise(async (resolve, reject) => {
    try {
      const {publicKey, total, infoProdutos} = await obterChavePublica();
      const mp = new window.MercadoPago(publicKey);

      const cardForm = mp.cardForm({
        amount: total,
        iframe: true,
        form: {
          id: "form-credit-card",
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
                description: infoProdutos,
                payer: {
                  email,
                  identification: {
                    type: identificationType,
                    number: identificationNumber,
                  },
                },
              }),
            }

            fetch("/payments/process_payment/", options)
            .then((response) => {
              if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
              }
              return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
            })
            .then((data) => {
              if (data.code == 200) {               
                window.location.href = "/payments/pagamento_concluido/";
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

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 10000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener("mouseenter", Swal.stopTimer);
      toast.addEventListener("mouseleave", Swal.resumeTimer);
    },
  });

// Função assíncrona para carregar o MercadoPago e criar o objeto
async function inicializarMercadoPagoPIX() {
  return new Promise(async (resolve, reject) => {
    try {
      const {publicKey, total, infoProdutos} = await obterChavePublica();
      const mp = new window.MercadoPago(publicKey);

      (async function getIdentificationTypes() {
        try {
          const identificationTypes = await mp.getIdentificationTypes();
          const identificationTypeElement = document.getElementById(
            "identificationType"
          );

          createSelectOptions(identificationTypeElement, identificationTypes);
        } catch (e) {
          return console.error("Error getting identificationTypes: ", e);
        }
      })();

      function createSelectOptions(
        elem,
        options,
        labelsAndKeys = { label: "name", value: "id" }
      ) {
        const { label, value } = labelsAndKeys;

        elem.options.length = 0;

        const tempOptions = document.createDocumentFragment();

        options.forEach((option) => {
          const optValue = option[value];
          const optLabel = option[label];

          const opt = document.createElement("option");
          opt.value = optValue;
          opt.textContent = optLabel;

          tempOptions.appendChild(opt);
        });

        elem.appendChild(tempOptions);
      }
      resolve();
    } catch (error) {
      reject(error);
    }
  });
}

async function data_qrcode() {
  const btn = document.querySelector("#form-pix");
  
  const {publicKey, total, infoProdutos} = await obterChavePublica();

  const options = {
    method: "POST", // Método HTTP que você deseja usar (neste caso, POST)
    headers: {
      "Content-Type": "application/json", // Tipo de conteúdo sendo enviado (JSON neste exemplo)
      "X-CSRFToken": CSRFToken,
    },
    body: JSON.stringify({
      payment_method_id: 'pix',
      transactionAmount: total,
      description: infoProdutos,
    }), // Converte os dados para JSON e os coloca no corpo da requisição
  };

  btn.addEventListener("click", (e) => {
    e.preventDefault();

    fetch("/payments/process_payment/", options)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      return response.json(); // Converte a resposta JSON em um objeto JavaScript (se a resposta for JSON)
    })
    .then((data) => {
      if (data.code == 200) {
        let data_book = data.book;
        let book = JSON.parse(data_book);
        Swal.showLoading();
        Swal.fire({
          icon: "info",
          title: `Pagamento via QR Code`,
          html: `<img src="data:image/jpeg;base64,${data.data.qrcode_base64}" alt="${book[0].fields.title}" style="width: 15rem;" />`,
          input: "text",
          inputLabel: "Código PIX copia e cola",
          inputValue: data.data.qrcode,
          confirmButtonText: "Copiar",
          confirmButtonColor: "#3085d6",
          showCancelButton: true,
          cancelButtonColor: "#d33",
          cancelButtonText: "Cancelar",
          allowOutsideClick: false, // Evita que o modal seja fechado ao clicar fora dele
          showCloseButton: true, // Exibe um botão de fechamento no modal
          width: "60vw",
          // Adicione o evento de copiar ao clicar no botão "Copiar"
          preConfirm: function () {
            document.querySelector("#swal2-input").select();
            document.execCommand("copy");
            // Use Swal.showValidationMessage para exibir a notificação sem fechar o modal
            Swal.showValidationMessage(
              "O código PIX foi copiado para a área de transferência."
            );
            // Adicione a classe CSS personalizada ao input
            document
              .querySelector("#swal2-input")
              .classList.add("remove-input-border");
          },
          customClass: {
            validationMessage: "custom-icon-validation", // Aplica a classe CSS personalizada ao ícone
          },
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
  });
}

inicializarMercadoPago()
inicializarMercadoPagoPIX()
data_qrcode()