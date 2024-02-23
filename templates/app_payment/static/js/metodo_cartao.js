export { getCardBrand, enviarProdutos };
// Cartão de Crédito

const btnCheckout = document.querySelector(".button-cta"),
  spiner = btnCheckout.querySelector(".spinner-border"),
  spinerCheckout = btnCheckout.querySelector(".spinerCheckout"),
  spinerLegenda = btnCheckout.querySelector(".spinerstatus");

window.addEventListener("pageshow", function (event) { // Função para adicionar a tela de carregamento
  if (event.persisted) {
    // A página está sendo carregada do cache do navegador (pelo botão de volta)
    spiner.classList.add("oculto");
    spinerLegenda.classList.add("oculto");
    spinerCheckout.classList.remove("oculto");
  }
});

$(function () { // Função em Jquery para verificsr se todos os campos estão preenchidos
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

    if (proceed) { // Caso esteja todos os dados preenchidos
      spiner.classList.remove("oculto");
      spinerLegenda.classList.remove("oculto");
      spinerCheckout.classList.add("oculto");

      const cardNumber = document.querySelector("#cardnumber");
      const numeroDoCartao = cardNumber.value.replace(/\s/g, "").toString();
      processarDadosCartao(numeroDoCartao);

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

async function recuperarImgBandeira(brand) { // Pega no BackEnd as imagens da bandeira do cartão
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

async function getCardBrand(numeroCartao) {// Função para verificar qual a bandeira do cartão (Em texto)
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

async function getInstallmentst(brand, valorTotal) {// Função que recebe a quantidade de parcelas, Calculo de juros e valor de cada parcela.
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

async function confConta() { // Função para receber a confirmação (ID) de Conta EFI (Gerencianet)
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

async function processarDadosCartao(cardnumber) { // Função para verificar os dados do cartão de crédito e receber token do pagamento
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
        reuse: true,
      })
      .getPaymentToken()
      .then((data) => {
        const payment_token = data.payment_token;
        const card_mask = data.card_mask;
        confChargeID(parcela, payment_token);

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

async function confChargeID(parcela, payment_token){ // Função para verificar se existe o chargeID no sessionStorage
  const pagamentoID = sessionStorage.getItem("charge_id");

  if (pagamentoID) {
    processesPayment(parcela, payment_token)
  } else {
    enviarProdutos(parcela, payment_token)
    
  }
}

async function enviarProdutos(parcela, payment_token) { // Função que envia os produtos para o BackEnd e para reenviar para o EFI e receber o ChargeID
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
      sessionStorage.setItem("errorpayment", false)
      processesPayment(parcela, payment_token)
    })
    .catch((error) => {
      console.error(error);
      Toast.fire({
        icon: "error",
        title: `Erro na requisição: ${error.message}`,
      });
    });
}

async function processesPayment(parcela, token) { // Função que enviar o token de pagamento e os dados pessoais para verificar o pagamento
  const cartID = document.querySelector("#cartid").textContent.replace("#", ""),
    CSRFToken = document.querySelector('input[name="csrfmiddlewaretoken').value;
  let charge_id = sessionStorage.getItem("charge_id");
  let erroPayment = sessionStorage.getItem("errorpayment");
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
      erropayment: erroPayment,
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
      if (data.code === 200) {
        statusPagamento(data, charge_id);
      } else {
        Toast.fire({
          icon: "error",
          title: "Error: " + data,
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

async function statusPagamento(status, cartID) { // Verifica o Status de pagamento de foi confirmado ou não
  if (status.code === 200) {
    switch (await status.data.status) {
      case "waiting":
        Toast.fire({
          icon: "warning",
          title: "Aguardando pagamento",
          text: "Aguardando a confirmação do pagamento",
        });
        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");

        sessionStorage.removeItem("errorpayment")
        break;
      case "approved":
        sessionStorage.removeItem("charge_id");
        sessionStorage.removeItem("errorpayment")
        window.location.href = "/payments/pagamentoconcluido/"+cartID;
        break;
      case "unpaid":
        spiner.classList.add("oculto");
        spinerLegenda.classList.add("oculto");
        spinerCheckout.classList.remove("oculto");

        Toast.fire({
          icon: "error",
          title: "Pagamento não realizado",
          text: status.data.refusal.reason,
        });

        sessionStorage.setItem("errorpayment", true)
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
