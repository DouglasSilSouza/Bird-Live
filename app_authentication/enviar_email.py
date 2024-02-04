from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import constant_time_compare
from django.conf import settings

class EnvioEmail:
    def __init__(self, user):
        self.user = user
    
    def enviandoEmail(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = self.user.activation_token

        activation_link = f'http://127.0.0.1:8000/authentication/activate/{uid}/{token}/'
        try:
            # Enviar e-mail de ativação
            subject = 'Ative sua conta'
            html_message = render_to_string('ecommerce_authentication/activation_email.html', {'user': self.user, 'activation_link': activation_link})
            email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [self.user.email])
            email.content_subtype = 'html'
            email.send()
            return True  # Adicionado para indicar sucesso
        except Exception as e:
            print(f"Erro ao enviar e-mail de ativação: {e}")
            return False  # Indicar falha no envio

    def activate_account(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist) as e:
            print(f"Erro ao ativar conta: {e}")
            user = None
        except Exception as e:
            print("Error: ", e)
            user = None

        # Verificar se o token de ativação é válido
        if user is not None and constant_time_compare(user.activation_token, token) and user.is_activation_token_valid():
            user.is_active = True
            user.save()
            return True
        else:
            return False
