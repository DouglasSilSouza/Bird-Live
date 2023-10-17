from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='e-home'),
    path('<int:id>', productOnly, name='productonly'),
    path('countcart', base, name='countcart'),
]