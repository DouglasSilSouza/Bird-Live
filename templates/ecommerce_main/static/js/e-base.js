function countCart() {
  const badges = document.querySelector("#badges"),
        tagHTML = document.createElement("span");
        tagHTML.classList.add("position-absolute");
        tagHTML.classList.add("top-0");
        tagHTML.classList.add("start-100");
        tagHTML.classList.add("translate-middle");
        tagHTML.classList.add("badge");
        tagHTML.classList.add("rounded-pill");
        tagHTML.classList.add("bg-danger");
        tagHTML.id = "badge";

  fetch("/countcart", {
    method: "GET",
  })
    .then(function (response) {
      return response.json();
    })
    .then((data) => {
        tagHTML.textContent = "";
        if (data.quantity > 0) {
            tagHTML.textContent = data.quantity;
        }
        badges.appendChild(tagHTML);
    })
    .catch((error) => {
      console.error(error);
    });
}

function navBar() {
  const toggle = document.querySelector('.navbar_toggle'),
        main = document.querySelector('main')
        nav = document.querySelector('.links');

  toggle.addEventListener('click', () => {
      console.log('clique');
      nav.classList.toggle('close');

      const body = document.body;
      if (nav.classList.contains('close')) {
          body.classList.remove('overflow');
      } else {
          body.classList.add('overflow');
      }
  });
}

function filtros() {
  const maisCem = document.querySelector('.maisCem'),
    menosCem = document.querySelector('.menosCem'),
    product = document.querySelectorAll('.product'),
    limpar = document.querySelector('.clean');

  product.forEach(item => {
    const btnPrice = item.querySelector('.btnPrice');
    const valorNumerico = parseFloat(btnPrice.textContent.replace("R$ ", "").replace(",", "."));
    

    maisCem.addEventListener('click', () => {
      if (valorNumerico <= 100) {
        item.classList.add('esconder');
      } else {
        item.classList.remove('esconder')
      }
    });

    menosCem.addEventListener('click', () => {
      if (valorNumerico >= 100) {
        item.classList.add('esconder');
      }else {
        item.classList.remove('esconder')
      }
    });

    limpar.addEventListener('click', () => {
      product.forEach(item => {
        item.classList.remove('esconder');
      });
    });
  });
}

const filter = document.querySelector('.filters');
if (filter && window.getComputedStyle(filter).display !== 'none') {
  filtros();
}

navBar();
countCart();
