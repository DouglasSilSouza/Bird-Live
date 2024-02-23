const pixModal = Swal.mixin({
  title: "Realize o pagamento via PIX",
  text: "Escaneie ou copie o código abaixo.",
});

const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  didOpen: (toast) => {
    toast.addEventListener("mouseenter", Swal.stopTimer);
    toast.addEventListener("mouseleave", Swal.resumeTimer);
  },
});

function base64ToBlob(base64, mime) {
  mime = mime || "";
  var sliceSize = 1024;
  var byteChars = window.atob(base64);
  var byteArrays = [];

  for (
    var offset = 0, len = byteChars.length;
    offset < len;
    offset += sliceSize
  ) {
    var slice = byteChars.slice(offset, offset + sliceSize);

    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    var byteArray = new Uint8Array(byteNumbers);

    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: mime });
}

export function payPix(opendivpix, closedivpix) {
  // Mostra a modal de carregamento
  const loadingModal = Swal.fire({
    title: "Carregando...",
    allowOutsideClick: false, // Evita que o usuário feche a modal clicando fora dela
    showConfirmButton: false,
    willOpen: () => {
      Swal.showLoading();
    },
  });

  const CSRFToken = document.querySelector(
      'input[name="csrfmiddlewaretoken'
    ).value,
    cartID = document.querySelector("#cartid").textContent.replace("#", "");
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRFToken,
    },
    body: JSON.stringify({ cartid: cartID }),
  };
  fetch("/payments/pay_pix", options)
    .then((response) => {
      return response.json().then((data) => {
        if (!response.ok) {
          const errorMessage = data.error_description || "Erro desconhecido";
          throw new Error(errorMessage);
        }
        return data;
      });
    })
    .then((data) => {
      // Fecha a modal de carregamento
      loadingModal.close();

      const dados = JSON.parse(data);
      let base64 = dados.imagemQrcode;
      let prefix = "data:image/png;base64,";
      if (base64.startsWith(prefix)) {
        base64 = base64.slice(prefix.length);
      }
      let blob = base64ToBlob(base64, "image/png");
      let imageUrl = URL.createObjectURL(blob);
      let inputvalue = dados.qrcode;

      // Exibe a modal do SweetAlert2 com os dados
      pixModal.fire({
          imageUrl: imageUrl,
          imageWidth: 250,
          imageHeight: 250,
          imageAlt: "QR Code PIX",
          input: "text",
          inputValue: inputvalue,
          inputAttributes: {
            readonly: true,
          },
          html: '<button id="copyButton" class="swal2-confirm swal2-styled">Copiar</button><p id="copyMessage"></p>',
          showConfirmButton: false,
          didOpen: () => {
            document
              .querySelector("#copyButton")
              .addEventListener("click", () => {
                navigator.clipboard.writeText(inputvalue);
                document.querySelector("#copyMessage").textContent = "Copiado!";
                document.querySelector("#copyMessage").style.color = "green";
              });
          },
        })
        .then((result) => {
          if (Swal.getCloseButton(result.dismiss)) {
            closedivpix.classList.remove("oculto");
            opendivpix.classList.add("oculto");
          }
        });
    })
    .catch((error) => {
      // Fecha a modal de carregamento em caso de erro
      loadingModal.close();

      console.error(error);
      Toast.fire({
        icon: "error",
        title: "Error: " + error.message,
      });
    });
}

function pagamentoConcluido(status, txid_status) {
  let tempoRestante = 10;
  console.log("Pagamento concluido")
  if (status === "CONCLUIDA") {
    pixModal.fire({
      icon: "success",
      title: "Pagamento realizado com sucesso",
      html: `<p>Agora você será redireconado para a página de confirmação de compra.</p><br><p>Tempo restante: <span id="tempoRestante">${tempoRestante}</span> segundos</p>`,
      allowOutsideClick: false, // Impede que o usuário feche clicando fora da modal
      showConfirmButton: false, // Não mostra botão de confirmação
      didOpen: () => {
        const interval = setInterval(() => {
          tempoRestante--;
          document.getElementById("tempoRestante").textContent = tempoRestante;

          // Verifica se o tempo acabou
          if (tempoRestante <= 0) {
            clearInterval(interval);

            window.location.href = "/payments/pagamentoconcluido/"+txid_status;
          }
        }, 1000); // Atualiza a cada segundo
      },
    });
  } else {
    pixModal.update({
      icon: "warning",
      title: "Houve um erro inesperado",
      text: "Não esperavamos outro Status, por favor tente novamente mais tarde",
    });
  }
}

const socket = new WebSocket(
  "wss://" + window.location.host + "/wss/notifications/"
);

socket.onopen = function(e) {
  console.log("Aberto: "+e)
}

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  pagamentoConcluido(data.status, data.txid_status);
  console.log("Dados recebido")
  console.log(data)
};

socket.onerror = function (erro) {
  console.error(erro);
};

socket.onclose = function () {
  console.log("Socket Fechado");
};
