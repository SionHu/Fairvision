from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html', {'title': 'About'})

def publication(request):
    return render(request, 'publication.html', {'title': 'Publication'})

def service(request):
    return render(request, 'service.html')

def serviceindex(request):
    return render(request, 'service-index.html')