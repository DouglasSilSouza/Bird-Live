from django.urls import path
from .views import *

urlpatterns = [
    path("", carrinho, name="cart"),
    path("getcart", getdatacart, name="getcart"),
    path("deleteitem", deletdatacart, name="deleteitem"),
]