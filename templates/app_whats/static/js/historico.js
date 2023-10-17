window.addEventListener('load', function() {
    var telefones = document.getElementsByClassName('telefone');
  
    for (var i = 0; i < telefones.length; i++) {
      var telefone = telefones[i].textContent;
      var telefoneFormatado = formatarTelefone(telefone);
      telefones[i].textContent = telefoneFormatado;
    }
  });
  
  function formatarTelefone(numero) {
    // Adicione a lógica aqui para formatar o número como desejar
    var codigoPais = numero.slice(0, 2);
    var ddd = numero.slice(2, 4);
    var prefixo = numero.slice(4, 9);
    var sufixo = numero.slice(9);
  
    return "+" + codigoPais + " (" + ddd + ") " + prefixo + "-" + sufixo;
  }