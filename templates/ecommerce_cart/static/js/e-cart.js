const containerResume = document.querySelectorAll(".resumecontainer"),
  totalElement = document.querySelector("#total"),
  valorTotal = document.querySelector("#valortotal");
let totalGeral = 0; // Variável global para o total geral

function atualizarBadge(oper, incremento) {
  const badge = document.querySelector("#badge");
  if (badge) {
    let contentBadge = badge.textContent;
    let formatBadge = parseInt(contentBadge, 10);

    if (isNaN(formatBadge)) {
      formatBadge = 0; // Defina um valor padrão se o conteúdo do badge for "NaN" ou vazio
    }

    switch (oper) {
      case "plus":
        formatBadge += incremento; // Incrementa o valor em 1
        break;

      case "dash":
        formatBadge -= incremento; // Subtrai o valor em 1
        break;

      default:
        break;
    }
    badge.textContent = formatBadge; // Atualiza o conteúdo do elemento HTML com o novo valor
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

function calcularTotalProduto(container) {
  const qtdText = container.querySelector(".quantity"),
    valoruni = container
      .querySelector(".valoruni")
      .textContent.replace(",", "."),
    subTotal = container.querySelector(".subvalorcalc");

  let convertvaloruni = parseFloat(valoruni);
  let qtd = parseInt(qtdText.textContent);

  let totalProduto = convertvaloruni * qtd;
  subTotal.textContent = formatCurrency(totalProduto);
  return totalProduto;
}

function atualizarTotalGeral() {
  totalGeral = 0; // Zere o total geral para recalculá-lo
  containerResume.forEach((container) => {
    totalGeral += calcularTotalProduto(container);
  });

  if (totalElement) {
    totalElement.textContent = formatCurrency(totalGeral);
    valorTotal.value = formatCurrency(totalGeral);
  }
}

function adicionarEventos(container) {
  const plus = container.querySelector(".plus"),
    dash = container.querySelector(".dash");

  plus.addEventListener("click", () => {
    let qtdText = container.querySelector(".quantity");
    let qtd = parseInt(qtdText.textContent);
    qtd++;
    qtdText.textContent = qtd;
    atualizarBadge("plus", 1);
    atualizarQuantidade(container);
    atualizarTotalGeral();
  });

  dash.addEventListener("click", () => {
    let qtdText = container.querySelector(".quantity");
    let qtd = parseInt(qtdText.textContent);
    if (qtd > 1) {
      qtd--;
      qtdText.textContent = qtd;
      atualizarBadge("dash", 1);
      atualizarQuantidade(container);
      atualizarTotalGeral();
    }
  });
}

function atualizarQuantidade(container) {
  let qtdText = container.querySelector(".quantity");
  let qtd = parseInt(qtdText.textContent);
  const idProdutoText = container.id;
  let idProduct = idProdutoText.split("product-")[1];

  fetch("/cart/atualizar_quantidade/", {
    method: "POST",
    body: JSON.stringify({ idProduto: idProduct, qtd: qtd }),
  })
    .then((response) => response.json())
    .then((data) => {})
    .catch((error) => {
      console.error(error.message);
    });
}

function removeProductCart() {
  const buttons = document.querySelectorAll(".btn-trash");

  buttons.forEach((button) => {
    button.addEventListener("click", (e) => {
      const idElement = button.id, // Obtém o ID do botão clicado
        section = document.querySelector(`#product-${idElement}`), // Seleciona a seção com o ID correspondente
        badge = document.querySelector("#badge");

      Swal.fire({
        title: "Deseja retirar esse produto do carrinho?",
        icon: "question",
        confirmButtonText: "Retirar",
        cancelButtonText: "Cancelar",
        showCancelButton: true,
        showCloseButton: true,
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire("Produto retirado!", "success");

          if ((section, badge)) {
            const qtdRemove = section.querySelector(".quantity"),
              currentBadgeValue = parseInt(badge.textContent),
              qtdToRemove = parseInt(qtdRemove.textContent);

            if (!isNaN(currentBadgeValue) && !isNaN(qtdToRemove)) {
              const newBadgeValue = currentBadgeValue - qtdToRemove;
              if (newBadgeValue === 0) {
                badge.textContent = "";
                window.location.reload();
              } else {
                badge.textContent = newBadgeValue.toString(); // Atualiza o conteúdo do elemento badge
              }
            }
            parseInt(badge.textContent) - parseInt(qtdRemove.textContent);
            if (qtdRemove) {
              section.remove(); // Remove a seção correspondente
            }
          }

          fetch("/cart/deleteitem/", {
            method: "POST",
            body: JSON.stringify({ idProduct: idElement }),
          })
            .then((response) => {
              return response.json();
            })
            .then((data) => {})
            .catch((error) => {
              console.error(error.message);
            });
        }
      });
    });
  });
}

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

const btnCheckout = document.querySelector("#checkout"),
  spiner = btnCheckout.querySelector('.spinner-border'),
  spinerCheckout = btnCheckout.querySelector('.spinerCheckout'),
  spinerLegenda = btnCheckout.querySelector('.spinerstatus');

  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        // A página está sendo carregada do cache do navegador (pelo botão de volta)
        spiner.classList.add('oculto');
        spinerLegenda.classList.add('oculto');
        spinerCheckout.classList.remove('oculto');
    }
});

btnCheckout.addEventListener("click", () => {
  spiner.classList.remove('oculto');
  spinerLegenda.classList.remove('oculto');
  spinerCheckout.classList.add('oculto');
  window.location.href = "/payments/pay";
});

document.addEventListener("DOMContentLoaded", function () {
  // Adicione manipuladores de eventos para todos os contêineres
  containerResume.forEach((container) => {
    adicionarEventos(container);
  });
  removeProductCart();
  atualizarTotalGeral();
});
