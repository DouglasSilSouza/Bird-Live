const juros = document.querySelector('.juros'),
    subtotalText = document.querySelector('.subtotal span').textContent,
    totalText = document.querySelector('.total span').textContent;

function calcularJuros() {
    const subtotal = parseFloat(subtotalText),
        total = parseFloat(totalText);

    let calc = (subtotal - total).toFixed(2);
    if (calc == 0) {
        juros.classList.add('oculto')
    } else {
        const jurosSpan = juros.querySelector('span');
        jurosSpan.textContent = calc
    }
}

calcularJuros()

