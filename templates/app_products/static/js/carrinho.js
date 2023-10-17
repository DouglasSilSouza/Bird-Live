import { inicializarMercadoPago } from "../../../app_payment/static/js/payment-card.js";
import { inicializarMercadoPagoPIX, data_qrcode } from "../../../app_payment/static/js/payment-pix.js";

const containerResume = document.querySelectorAll(".resumecontainer");
const totalElement = document.querySelector("#total");
const valorTotal = document.querySelector("#valortotal");
let totalGeral = 0; // Variável global para o total geral

function calcularTotalProduto(container) {
  const qtdText = container.querySelector(".quantity");
  const valoruni = container.querySelector(".valoruni").innerText;

  let convertvaloruni = parseFloat(valoruni.replace(",", "."));
  let qtd = parseInt(qtdText.textContent);

  let totalProduto = convertvaloruni * qtd;
  return totalProduto;
}

function atualizarTotalGeral() {
    
  totalGeral = 0; // Zere o total geral para recalculá-lo
  containerResume.forEach((container) => {
    totalGeral += calcularTotalProduto(container);
  });

  totalElement.textContent = totalGeral.toLocaleString("pt-BR");
  valorTotal.value = totalGeral.toLocaleString("pt-BR");

}

function adicionarEventos(container) {
  const plus = container.querySelector(".plus");
  const dash = container.querySelector(".dash");

  plus.addEventListener("click", () => {
    let qtdText = container.querySelector(".quantity");
    let qtd = parseInt(qtdText.textContent);
    qtd++;
    qtdText.textContent = qtd;
    atualizarTotalGeral();
  });

  dash.addEventListener("click", () => {
    let qtdText = container.querySelector(".quantity");
    let qtd = parseInt(qtdText.textContent);
    if (qtd > 1) {
      qtd--;
      qtdText.textContent = qtd;
      atualizarTotalGeral();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  // Adicione manipuladores de eventos para todos os contêineres
  containerResume.forEach((container) => {
    adicionarEventos(container);
  });
  atualizarTotalGeral();
  inicializarMercadoPago();
  inicializarMercadoPagoPIX();
  data_qrcode()
});
