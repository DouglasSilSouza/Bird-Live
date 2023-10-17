function limitado() {
    const elementos = document.querySelectorAll('.limited');
        
    elementos.forEach(function(elemento) {
        let lineHeight = parseInt(window.getComputedStyle(elemento).lineHeight);
        let maxHeight = lineHeight * 2; // Duas linhas
        
        if (elemento.scrollHeight > maxHeight) {
            while (elemento.scrollHeight > maxHeight) {
                elemento.textContent = elemento.textContent.replace(/\W*\s(\S)*$/, '...');
            }
        }
    });
}

limitado()