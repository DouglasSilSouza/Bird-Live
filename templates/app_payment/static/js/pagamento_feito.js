function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

document.addEventListener("DOMContentLoaded", function () {
  const currencies = document.querySelectorAll(".currency");
  currencies.forEach((element) => {
    const value = parseFloat(element.textContent.replace("R$", "").trim());
    element.textContent = formatCurrency(value);
  });
});
