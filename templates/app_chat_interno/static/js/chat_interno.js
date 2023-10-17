function verificarEnvio(event) {
    if (event.keyCode === 13 && !event.shiftKey) {
      document.getElementById('formMensagem').submit(); // Envia o formulário manualmente
    }
  }
  
  function adicionarMensagem(event) {
    if (event && event.keyCode === 13 && event.shiftKey) {
      // Verifica se foi pressionado Enter + Shift
      adicionarQuebraDeLinha(event);
    } else if (event && event.keyCode === 13) {
      // Verifica se foi pressionado apenas Enter
      event.preventDefault()
      enviarMensagem();
    }
  }
  
  function adicionarQuebraDeLinha(event) {
    var textarea = document.getElementById('meuTextarea');
    textarea.value += '\n'; // Adiciona uma quebra de linha
    textarea.style.height = 'auto'; // Redefine a altura para permitir recalcular corretamente
    // Define a altura do textarea com base no conteúdo e em um limite máximo
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    textarea.scrollTop = textarea.scrollHeight;
    // Não é necessário chamar event.preventDefault() aqui
  }
  
  function enviarMensagem() {
  
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer)
        toast.addEventListener('mouseleave', Swal.resumeTimer)
      }
    })
  
    var numeroTelefone = document.getElementById('numeroUsuario').dataset.numero;
    var textarea = document.getElementById('meuTextarea');
    var chatMessages = document.getElementById('chat');
    var mensagem = textarea.value.trim();
  
    if (mensagem !== '') {
      var mensagemHTML = '<div class="message origem" name="origem">' + formatarQuebraDeLinha(mensagem) + '</div>';
      chatMessages.innerHTML += mensagemHTML;
      textarea.value = '';
      textarea.style.height = 'auto';
      chatMessages.scrollTop = chatMessages.scrollHeight;
      textarea.scrollTop = 0;
  
      fetch('/send_whatsapp_message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({numero: numeroTelefone, mensagem: mensagem })
      })
      .then(response => response.json())
      .then(data => {
        // Verifique a resposta do servidor
        if (data.status_icon == '200') {
          Toast.fire({
            icon: 'success',
            title: data.mensagem
          });
        } else {
          Toast.fire({
            icon: 'error',
            title: data.mensagem
          });
        }
      })
      .catch(error => {
        // Lide com erros de requisição
        Toast.fire({
          icon: 'error',
          title: 'Erro ao enviar a mensagem' + error
        });
      });
    }
  }
  
  // Adicione eventos de teclado e clique aos elementos correspondentes
  document.getElementById('meuTextarea').addEventListener('keydown', adicionarMensagem);
  document.getElementById('enviarIcone').addEventListener('click', enviarMensagem);

  let url = `ws://${window.location.host}/ws/socket-server/`

  const chatSocket = new WebSocket(url)

  chatSocket.onopen = function(e) {
    console.log('Conexão WebSocket estabelecida.');
  };

  chatSocket.onmessage = function(e){
      let data = JSON.parse(e.data)
      console.log('Data:', data.message)

      if(data.type === 'chat'){
          let messages = document.getElementById('messages')

          messages.insertAdjacentHTML('beforeend', `<div>
                                  <p>${data.message}</p>
                              </div>`)
      }
  }

  let form = document.getElementById('formMensagem')
  form.addEventListener('submit', (e)=> {
      e.preventDefault()
      let message = e.target.message.value 
      chatSocket.send(JSON.stringify({
          'message':message
      }))
      form.reset()
  })

  chatSocket.onclose = function(e) {
    // Lide com o fechamento da conexão WebSocket, se necessário
    console.error('Conexão WebSocket fechada inesperadamente.');
  }
