function verificarEnvio(event) {
  if (event.keyCode === 13 && !event.shiftKey) {
    document.getElementById('formMensagem').submit(); // Envia o formulário manualmente
  }
}

function adicionarQuebraDeLinha(event) {
  var textarea = document.getElementById('meuTextarea');
  var mensagem = textarea.value + '\n'; // Adiciona uma quebra de linha
  textarea.value = mensagem;
  textarea.style.height = 'auto'; // Redefine a altura para permitir recalcular corretamente
  // Define a altura do textarea com base no conteúdo e em um limite máximo
  textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
  textarea.scrollTop = textarea.scrollHeight;
  // Não é necessário chamar event.preventDefault() aqui

  return mensagem; // Retorna a mensagem atualizada
}

var numeroTelefone = document.getElementById('numeroUsuario').dataset.numero;
let chatSocket = new WebSocket('wss://' + window.location.host + '/ws/conversa/' + numeroTelefone + "/" );

chatSocket.onopen = function(e) {
  console.log('Conexão WebSocket estabelecida.');
};

function exibirMensagemRecebida(mensagem, time) {
  var chatMessages = document.getElementById('chat');

  var mensagemHTML = '<div class="message"><span class="time_message">' + time + '</span><p>' + mensagem + '</p></div>';
  chatMessages.innerHTML += mensagemHTML;
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function exibirImagemRecebida(imagem, time, type_arq) {
  var chatMessages = document.getElementById('chat');

  var mensagemHTML = `<div class="message">
                        <span class="time_message">${time}</span>
                        <img src="data:${type_arq};base64,${imagem}" class="imagem_destinatario" alt="Imagem">
                      </div>`;

  chatMessages.innerHTML += mensagemHTML;
  chatMessages.scrollTop = chatMessages.scrollHeight;
}


function atualizarStatus(status, wa_id_message, error) {
  var iconStatus = document.querySelector('[id="' + wa_id_message + '"]');
  if (iconStatus !== null) { // Verifica se o elemento existe
    switch (status) {
      case 'sent':
        // Remove todas as classes existentes do ícone
        iconStatus.classList.remove('bi-clock', 'bi-check-all', 'azul');
        // Adiciona a classe do ícone de check
        iconStatus.classList.add('bi-check');
        break;
      case 'delivered':
        // Remove todas as classes existentes do ícone
        iconStatus.classList.remove('bi-clock', 'bi-check', 'azul');
        // Adiciona a classe do ícone de check duplo
        iconStatus.classList.add('bi-check-all');
        break;
      case 'read':
        // Remove todas as classes existentes do ícone
        iconStatus.classList.remove('bi-clock', 'bi-check', 'bi-check-all');
        // Adiciona as classes do ícone de check duplo azul
        iconStatus.classList.add('bi-check-all', 'azul');
        break;
      case 'failed':
        // Remove todas as classes existentes do ícone
        iconStatus.classList.remove('bi-clock', 'bi-check', 'bi-check-all', 'bi-check-all', 'azul');
        // Adiciona as classes do ícone de check duplo azul
        iconStatus.classList.add('bi-exclamation-triangle', 'red');

        if (conteudo_erro !== null) {

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
  
          var conteudo_erro = JSON.parse(error)
  
          Toast.fire({
            icon: 'error',
            title: conteudo_erro.title,
            text: `${conteudo_erro.details} | ${conteudo_erro.code}`
          });

        }

        break;
    }
  }
}


chatSocket.onmessage = function(event) {
  let data = JSON.parse(event.data);
  switch (data.type_conteudo){
    case 'text':
      let message = data['message'];
      let numerotelefone = data['numerotelefone'];
      let hora_back = data['hora_back'];
        
      if (message && message.trim() !== '') {
        exibirMensagemRecebida(message, hora_back);
      }
      break;
    
    case 'image':
      let image_data = data['image_data'];
      let numero_telefone = data['numerotelefone'];
      let hora_back_time = data['hora_back'];
      let type_arq =data['type_arq'];
        
      if (image_data && image_data.trim() !== '') {
        exibirImagemRecebida(image_data, hora_back_time, type_arq);
      }
      break;
    
    case 'statuses':
      var status = data['status'];
      var wa_id_message = data['wa_id_message'];
      var error = data['error'];

      if (status && status.trim() !== '') {
        atualizarStatus(status, wa_id_message, error);
      }
      break;
  }
};

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

// Obtém a hora e a data atual
var dataAtual = new Date();

// Formata a data e a hora
var dataFormatada = dataAtual.toLocaleDateString(); // Formata a data no formato local (ex: 23/06/2023)
var horaFormatada = dataAtual.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}); // Formata a hora no formato local (ex: 09:30)

function previewImage() {
  var fileInput = document.getElementById('files');
  var file = fileInput.files[0];
  var thumbnail = document.getElementById('thumbnail-container');

  if (file) {
    var reader = new FileReader();

    reader.onload = function(e) {
      var imageUrl = e.target.result;

      thumbnail.innerHTML = `
        <i class="icon fas fa-xmark" id="fechar_icon"></i>
        <img src="${imageUrl}" alt="Thumbnail" style="width: 100%;">
      `;

      thumbnail.classList.remove('hidden');
      thumbnail.classList.add('thumbnail');

      var fecharIcon = document.getElementById('fechar_icon');
      fecharIcon.addEventListener('click', function() {
        thumbnail.classList.add('hidden');
        thumbnail.classList.remove('thumbnail');
        thumbnail.innerHTML = '';
        fileInput.value = null; // Limpa o valor do campo de entrada de arquivo
      });
    };

    reader.readAsDataURL(file);
  } else {
    thumbnail.innerHTML = '';
  }

  return file;
}

document.getElementById('files').addEventListener('change', previewImage);

const emojiButton = document.getElementById('emoji-button');
var textarea = document.getElementById('meuTextarea');
let picker = null;

// Função para abrir o seletor de emojis ou fechá-lo
emojiButton.addEventListener('click', () => {
  if (!picker || !document.body.contains(picker)) {
    const pickerOptions = { 
      onEmojiSelect: (emoji) => {
        const cursorPosition = textarea.selectionStart;
        const text = textarea.value;
        const newText = text.slice(0, cursorPosition) + emoji.native + text.slice(cursorPosition);
        textarea.value = newText;
      }
    };
    
    picker = new EmojiMart.Picker(pickerOptions);
    document.body.appendChild(picker);
  } else {
    picker.remove();
    picker = null;
  }
});

function enviarMensagem() {
  
  var chatMessages = document.getElementById('chat');
  var mensagem = textarea.value.trim();

  var fileInput = document.getElementById('files');
  var file = fileInput.files[0];
  var filePath = fileInput.value;
  var thumbnail = document.getElementById('thumbnail-container');

  if (mensagem !== '') {

    var mensagemHTML = '<div class="message origem" name="origem"> <p>' + adicionarQuebraDeLinha(mensagem) + '</p><span class="time_message">'+ horaFormatada +'</span></div>';
    chatMessages.innerHTML += mensagemHTML;
    textarea.value = '';
    textarea.style.height = 'auto';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    textarea.scrollTop = 0;
    var conteudo = mensagem
    var type_conteudo = 'text'
  }

  if (file !== undefined) {
    var reader = new FileReader();

    reader.onload = function(e) {
      var imageUrl = e.target.result;

      var mensagemHTML = `<div class="message origem" name="origem">
                            <img src="${imageUrl}" class="imagem_remetente" alt="Imagem">
                            <span class="time_message">${horaFormatada}</span>
                          </div>`;
      chatMessages.innerHTML += mensagemHTML;
      chatMessages.scrollTop = chatMessages.scrollHeight;
      textarea.scrollTop = 0;

      thumbnail.classList.add('hidden');
      thumbnail.classList.remove('thumbnail');
      thumbnail.innerHTML = '';
      fileInput.value = null; // Limpa o valor do campo de entrada de arquivo

      var conteudo = JSON.stringify({codeimage: imageUrl, pathimage: filePath});
      var type_conteudo = 'image';

      // Enviar a imagem para o backend
      enviarConteudo(conteudo, type_conteudo);
    };

    reader.readAsDataURL(file);
    return;
  }

  // Adicione este bloco de código para enviar o áudio gravado
  if (audioBlob !== undefined) {
    var formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');
    formData.append('type_conteudo', 'audio');
    formData.append('datahora', dataFormatada + ' ' + horaFormatada);

    var mensagemHTML = `<div class="message origem" name="origem">
                            <audio src="${audioBlob}" id="audioPlayer" controls></audio>
                            <span class="time_message">${horaFormatada}</span>
                          </div>`;
      chatMessages.innerHTML += mensagemHTML;
      chatMessages.scrollTop = chatMessages.scrollHeight;
      textarea.scrollTop = 0;

    console.log(`Audio: ${formData}`)
  }

  // Enviar a mensagem de texto para o backend
  enviarConteudo(conteudo, type_conteudo);
}

function enviarConteudo(conteudo, type_conteudo) {
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

  if (type_conteudo !== '') {

    fetch('/send_whatsapp_message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        numero: numeroTelefone,
        mensagem: conteudo,
        type_conteudo: type_conteudo,
        datahora: dataFormatada+' '+horaFormatada
      })
    })
    .then(response => response.json())
    .then(data => {
      // Verifique a resposta do servidor
      if (data.status_response == '200') {

        // Atualize o template com o novo elemento do ícone
        var chatMessages = document.getElementById('chat');
        var novoIcone = document.createElement('i');
        novoIcone.id = data.wa_id_message;
        novoIcone.classList.add('bi', 'bi-clock');
        chatMessages.lastChild.appendChild(novoIcone); // Adicione o novo ícone ao último elemento da lista de mensagens

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
        title: 'Erro' + error
      });
    });
  }
}

/* function enviarMensagem() {

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

  var textarea = document.getElementById('meuTextarea');
  var chatMessages = document.getElementById('chat');
  var mensagem = textarea.value.trim();

  var fileInput = document.getElementById('files');
  var file = fileInput.files[0];

  if (mensagem !== '') {
    var mensagemHTML = '<div class="message origem" name="origem"> <p>' + adicionarQuebraDeLinha(mensagem) + '</p><span class="time_message">'+ horaFormatada +'</span></div>';
    chatMessages.innerHTML += mensagemHTML;
    textarea.value = '';
    textarea.style.height = 'auto';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    textarea.scrollTop = 0;
    var conteudo = mensagem
    var type_conteudo = 'text'
  
  } else if (file !== ''){
    var get_image = document.getElementById('files').addEventListener('change', previewImage);
    var mensagemHTML = `<div class="message origem" name="origem"><img src="${get_image}" class="imagem_destinatario" alt="Imagem"><span class="time_message">${horaFormatada}</span></div>`;
    chatMessages.innerHTML += mensagemHTML;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    textarea.scrollTop = 0;
    var conteudo = get_image
    var type_conteudo = 'image'
  }

    fetch('/send_whatsapp_message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({numero: numeroTelefone, mensagem: conteudo, type_conteudo: type_conteudo, datahora: dataFormatada+' '+horaFormatada})
    })
    .then(response => response.json())
    .then(data => {
      // Verifique a resposta do servidor
      if (data.status_response == '200') {

        // Atualize o template com o novo elemento do ícone
        var chatMessages = document.getElementById('chat');
        var novoIcone = document.createElement('i');
        novoIcone.id = data.wa_id_message;
        novoIcone.classList.add('bi', 'bi-clock');
        chatMessages.lastChild.appendChild(novoIcone); // Adicione o novo ícone ao último elemento da lista de mensagens

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
        title: 'Erro' + error
      });
    });
};
 */

chatSocket.onclose = function(e) {
  // Lide com o fechamento da conexão WebSocket, se necessário
  console.error('Conexão WebSocket fechada inesperadamente.');
};

// Adicione eventos de teclado e clique aos elementos correspondentes
document.getElementById('meuTextarea').addEventListener('keydown', adicionarMensagem);
document.getElementById('enviarIcone').addEventListener('click', enviarMensagem);

var btn_finalizar = document.getElementById('botão_finalizar').addEventListener('click', finalizar_atendimento);

function finalizar_atendimento(){
  botao_fim = True
  fetch('/finalizar_conversa/', {
    method: 'POST',
    body: JSON.stringify({botao_fim: botao_fim})
  })
  .then(response => response.json())
  .then(data => {
    // Verifique a resposta do servidor
    if (data.status_response == '200') {
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
      title: 'Erro' + error
    });
  });
}

const bolha = document.getElementById('bolha');
const icons = document.querySelectorAll('.i_chat');
const icon1 = document.getElementById('icon1');
const icon2 = document.getElementById('icon2');
const icon3 = document.getElementById('icon3');
const icon4 = document.getElementById('icon4');

function toggleBolha() {
  const isBolhaVisible = bolha.classList.contains('bolha_show');

  if (isBolhaVisible) {
    bolha.classList.remove('bolha_show');
    icon1.classList.remove('icon1_show')
    icon2.classList.remove('icon2_show')
    icon3.classList.remove('icon3_show')
    icons.forEach(icon => {
      icon.classList.add('hidden');
    });
    icon4.classList.remove('rotated');
  } else {
    bolha.classList.add('bolha_show');
    icon1.classList.add('icon1_show')
    icon2.classList.add('icon2_show')
    icon3.classList.add('icon3_show')
    icons.forEach(icon => {
      icon.classList.remove('hidden');
    });
    icon4.classList.add('rotated');
  }
}

function resizeHandler() {
  const screenWidth = window.innerWidth;

  if (screenWidth <= 768) {
    bolha.style.display = 'block';
    icons.forEach(icon => {
      icon.classList.remove('hidden');
    });
    icon4.classList.remove('rotated');
  } else {
    bolha.style.display = 'none';
    bolha.style.height = '0';
    icons.forEach(icon => {
      icon.classList.remove('hidden');
    });
    icon4.classList.remove('rotated');
  }
}

window.addEventListener('resize', resizeHandler);
icon4.addEventListener('click', toggleBolha);
