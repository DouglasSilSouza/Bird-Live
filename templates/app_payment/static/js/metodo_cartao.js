export { getCardBrand, enviarProdutos };
// Cartão de Crédito

const btnCheckout = document.querySelector(".button-cta"),
  spiner = btnCheckout.querySelector(".spinner-border"),
  spinerCheckout = btnCheckout.querySelector(".spinerCheckout"),
  spinerLegenda = btnCheckout.querySelector(".spinerstatus");

window.addEventListener("pageshow", function (event) {
  if (event.persisted) {
    // A página está sendo carregada do cache do navegador (pelo botão de volta)
    spiner.classList.add("oculto");
    spinerLegenda.classList.add("oculto");
    spinerCheckout.classList.remove("oculto");
  }
});

$(function () {
  $("#cardnumber").payment("formatCardNumber");
  $("#cardexpiration").payment("formatCardExpiry");
  $("#cardcvc").payment("formatCardCVC");

  $("#cardnumber").keyup(function (event) {
    $("#label-cardnumber").empty().append($(this).val());
  });

  $("#cardexpiration").keyup(function (event) {
    var data = $(this).val() + "<span>" + $("#cardcvc").val() + "</span>";
    $("#label-cardexpiration").empty().append(data);
  });

  $("#cardcvc").keyup(function (event) {
    var data =
      $("#cardexpiration").val() + "<span>" + $(this).val() + "</span>";
    $("#label-cardexpiration").empty().append(data);
  });

  $(".button-cta").on("click", function () {
    var proceed = true;
    $(".field input").each(function () {
      $(this)
        .parent()
        .find("path")
        .each(function () {
          $(this).attr("fill", "#dddfe6");
        });

      if (!$.trim($(this).val())) {
        $(this)
          .parent()
          .find("path")
          .each(function () {
            $(this).attr("fill", "#f1404b");
            proceed = false;
          });

        if (!proceed) {
          $(this).parent().find("svg").animate({ opacity: "0.1" }, "slow");
          $(this).parent().find("svg").animate({ opacity: "1" }, "slow");
          $(this).parent().find("svg").animate({ opacity: "0.1" }, "slow");
          $(this).parent().find("svg").animate({ opacity: "1" }, "slow");
        }
      }
    });

    if (proceed) {
      spiner.classList.remove("oculto");
      spinerLegenda.classList.remove("oculto");
      spinerCheckout.classList.add("oculto");

      const cardNumber = document.querySelector("#cardnumber");
      const numeroDoCartao = cardNumber.value.replace(/\s/g, "").toString();
      getToken(numeroDoCartao);
      //everything looks good! proceed purchase...
      //   $(".field")
      //     .find("path")
      //     .each(function () {
      //       $(this).attr("fill", "#3ac569");
      //     });
      //   $(".payment").fadeToggle("slow", function () {
      //     $(".paid").fadeToggle("slow", "linear");
      //   });
    }
  });
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

// Função para carregar e manipular o arquivo JSON
async function recuperarImgBandeira(brand) {
  const imgHTML = document.querySelector("#bandeiracartao"),
    CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRFToken,
    },
    body: JSON.stringify({ bandeira: brand }),
  };

  fetch("/payments/flag", options)
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
      if (data.flag.image) {
        imgHTML.classList.remove("oculto");
        imgHTML.setAttribute("src", data.flag.image.toString());
      }
    })
    .catch((error) => {
      console.error(error);
      Toast.fire({
        icon: "error",
        title: "Error: " + error.message,
      });
    });
}

async function getCardBrand(numeroCartao) {
  const totalText = document
      .querySelector("#total")
      .textContent.replace("R$", "")
      .replace(",", ""),
    total = parseInt(totalText);

  try {
    const brand = await EfiJs.CreditCard.setCardNumber(numeroCartao)
      .verifyCardBrand()
      .then((brand) => {
        if (brand !== "undefined") {
          //console.log("Bandeira: ", brand);
          recuperarImgBandeira(brand);
          getInstallmentst(brand, total);
          return brand;
        }
      })
      .catch((err) => {
        console.error(err);
        console.log("Código: ", err.code);
        console.log("Nome: ", err.error);
        console.log("Mensagem: ", err.error_description);
      });
    return brand;
  } catch (error) {
    console.error(error);
    console.log("Código: ", error.code);
    console.log("Nome: ", error.error);
    console.log("Mensagem: ", error.error_description);
  }
}

async function getInstallmentst(brand, valorTotal) {
  const result = await confConta(),
    select = document.querySelector("#parcelas");
  try {
    EfiJs.CreditCard.setAccount(result)
      .setEnvironment("sandbox")
      .setBrand(brand)
      .setTotal(valorTotal)
      .getInstallments()
      .then((parcelas) => {
        //console.log("Parcelas", parcelas.installments);
        if (parcelas) {
          select.disabled = false;

          const numeroMaximoParcelas = 10;
          const arrayParcelas = Array.from(
            { length: numeroMaximoParcelas },
            (_, i) => i + 1
          );

          const options = arrayParcelas.map((parcela) => {
            const valorParcela = parcelas.installments[parcela - 1]; // Acesse a parcela correta
            const valorFormatado = valorParcela.currency || valorParcela; // Trate possível erro de propriedade
            return `<option value="${parcela}">${parcela}x de R$ ${valorFormatado}</option>`;
          });

          select.innerHTML = options.join("");
        }
      })
      .catch((err) => {
        console.error(err);
        console.log("Código: ", err.code);
        console.log("Nome: ", err.error);
        console.log("Mensagem: ", err.error_description);

        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");

        Toast.fire({
          icon: "error",
          title: "Error: " + err.error_description,
        });
      });
  } catch (error) {
    console.error(error);
    console.log("Código: ", error.code);
    console.log("Nome: ", error.error);
    console.log("Mensagem: ", error.error_description);

    spiner.classList.add("oculto");
    spinerLegenda.classList.add("oculto");
    spinerCheckout.classList.remove("oculto");

    Toast.fire({
      icon: "error",
      title: "Error: " + error.error_description,
    });
  }
}

async function confConta() {
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetch("/payments/conf_conta", options)
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
      return data.count;
    })
    .catch((error) => {
      spiner.classList.add("oculto");
      spinerLegenda.classList.add("oculto");
      spinerCheckout.classList.remove("oculto");
      console.error(error);
      Toast.fire({
        icon: "error",
        title: "Error: " + error.message,
      });
    });
}

async function getToken(cardnumber) {
  const cvvText = document.querySelector("#cardcvc").value,
    cvv = cvvText.toString(),
    vencimento = document.querySelector("#cardexpiration"),
    parcela = document.querySelector("#parcelas").value;

  const venc = vencimento.value.replace(/\s/g, "").split("/"),
    year = venc[1],
    month = venc[0];

  const result = await confConta();
  const brand = await getCardBrand(cardnumber);

  try {
    const token = await EfiJs.CreditCard.setAccount(result)
      .setEnvironment("sandbox") // 'production' or 'sandbox'
      .setCreditCardData({
        brand: brand,
        number: cardnumber,
        cvv: cvv,
        expirationMonth: month,
        expirationYear: year,
        reuse: false,
      })
      .getPaymentToken()
      .then((data) => {
        const payment_token = data.payment_token;
        const card_mask = data.card_mask;
        PayCartao(parcela, payment_token);

        return payment_token;
      })
      .catch((err) => {
        console.log("Código: ", err.code);
        console.log("Nome: ", err.error);
        console.log("Mensagem: ", err.error_description);

        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");

        Toast.fire({
          icon: "error",
          title: err.error_description,
        });
      });
    return token;
  } catch (error) {
    console.log("Código: ", error.code);
    console.log("Nome: ", error.error);
    console.log("Mensagem: ", error.error_description);

    spiner.classList.add("oculto");
    spinerLegenda.classList.add("oculto");
    spinerCheckout.classList.remove("oculto");

    Toast.fire({
      icon: "error",
      title: error.error_description,
    });
  }
}

function PayCartao(parcela, token) {
  const cartID = document.querySelector("#cartid").textContent.replace("#", ""),
    CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;
  let charge_id = sessionStorage.getItem("charge_id");
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRFToken,
    },
    body: JSON.stringify({
      parcela: parcela,
      token: token,
      carrinhoid: cartID,
      charge_id: charge_id,
    }),
  };

  fetch("/payments/conclusao_pagamento_cartao", options)
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
      if (data.dados.code === 200){
        statusPagamento(data, sessionStorage.getItem("charge_id"));
      } else {
        Toast.fire({
          icon: "error",
          title: "Error Data: " + data,
        });
      }

    })
    .catch((erro) => {
      spiner.classList.add("oculto");
      spinerLegenda.classList.add("oculto");
      spinerCheckout.classList.remove("oculto");
      console.error(erro);
      Toast.fire({
        icon: "error",
        title: erro,
      });
    });
}

function statusPagamento(status, cartID) {
  console.log(status)
  if (status.code ===200){
    switch (status.data.status) {
      case "waiting":
        Toast.fire({
          icon: "warning",
          title: "Aguardando pagamento",
          text: "Aguardando a confirmação do pagamento"
        });
        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");
        break;
      case "approved":
        Toast.fire({
          icon: "success",
          title: "Pagamento realizado com sucesso",
        });
        sessionStorage.removeItem("charge_id");
        //window.location.href = "/payments/pagamentoconcluido/"+cartID;
        break;
      case "unpaid":
        Toast.fire({
          icon: "error",
          title: "Pagamento não realizado",
          text: status.data.refusal.reason
        });
        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");
    }
  } else {
    Toast.fire({
      icon: "error",
      title: "Pagamento recusado",
    });
    spiner.classList.add("oculto");
    spinerLegenda.classList.add("oculto");
    spinerCheckout.classList.remove("oculto");
  }
}

async function enviarProdutos() {
  const cartID = document.querySelector("#cartid").textContent.replace("#", ""),
    CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRFToken,
    },
    body: JSON.stringify({ carrinhoid: cartID }),
  };

  fetch("/payments/pay_cartao", options)
    .then((response) => {
      return response.json().then((data) => {
        if (!response.ok) {
          const errorMessage = data.erro || "Erro desconhecido";
          throw new Error(errorMessage);
        }
        return data;
      });
    })
    .then((data) => {
      sessionStorage.setItem("charge_id", data.charge_id);
    })
    .catch((error) => {
      console.error(error);
      Toast.fire({
        icon: "error",
        title: `Erro na requisição: ${error.message}`,
      });
    });
}
