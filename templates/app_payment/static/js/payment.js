import { payPix } from "./metodo_pix.js";
import {  getCardBrand, enviarProdutos } from "./metodo_cartao.js";

const cardElements = document.querySelectorAll(".nav-link");

function toggleCard(element) {
  element.addEventListener("click", () => {
    cardElements.forEach((card) => {
      if (card !== element) {
        card.classList.remove("active");
        const targetId = card.getAttribute("data-target");
        const targetElement = document.getElementById(targetId);
        targetElement.classList.add("oculto");
      }
    });

    const targetId = element.getAttribute("data-target");
    const targetElement = document.getElementById(targetId);

    if (!element.classList.contains("active")) {
      element.classList.add("active");
      targetElement.classList.remove("oculto");

      switch (targetId) {
        case "bodypix":
          const closedivpix = targetElement.querySelector(".close"),
            opendivpix = targetElement.querySelector(".open"),
            tryBtn = closedivpix.querySelector(".trypix");
          closedivpix.classList.add("oculto");
          opendivpix.classList.remove("oculto");
          if (tryBtn) {
            tryBtn.addEventListener("click", () => {
              payPix(opendivpix, closedivpix);
            });
          }
          payPix(opendivpix, closedivpix);
          break;

        case "bodycartao":
          limitarCaracteres(targetElement);
          const cardNumber = document.querySelector("#cardnumber");         
          cardNumber.addEventListener('input', async function() {
            if (cardNumber.value.replace(/\s/g, "") >= 16){
              const numeroDoCartao = cardNumber.value.replace(/\s/g, "").toString();
              await getCardBrand(numeroDoCartao);
            }
          });
          break;
      }
    } else {
      element.classList.remove("active");
      targetElement.classList.add("oculto");
    }
  });
}

function limitarCaracteres(element) {
  var paragrafos = element.querySelectorAll(".tituloprod");
  var limiteCaracteres = 20;

  paragrafos.forEach(function (elemento) {
    if (elemento.textContent.length > limiteCaracteres) {
      var textoLimitado = elemento.textContent.substring(0, limiteCaracteres);
      elemento.textContent = textoLimitado + "...";
    }
  });
}

cardElements.forEach((card) => {
  toggleCard(card);
});
