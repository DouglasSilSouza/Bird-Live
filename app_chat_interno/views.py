from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def chat_interno(request):
    return render (request, 'app_chat_interno/chat_interno.html')