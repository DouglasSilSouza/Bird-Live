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
      if (!response.ok) {
        throw new Error(
          Toast.fire({
            icon: "error",
            title: `Erro na requisição: ${response.status}`,
          })
        );
      }
      return response.json();
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
      Swal.fire({
        title: "Realize o pagamento via PIX",
        text: "Escaneie ou copie o código abaixo.",
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
      }).then((result) => {
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

