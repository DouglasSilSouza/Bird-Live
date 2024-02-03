from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('login_colab/', login_view_colab, name='login_colab'),
    path('cadastro_collaborator/', cadastro_colaborador, name='cadastro_collaborator'),
    path('cadastro_user/', cadastro_usuario, name='cadastro_user'),
    path('logout/', logout_view, name='logout_view'),
    path('configuracoes/', configuracoes, name='configuracoes'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]