from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', chat_interno, name='chat_interno'),
]