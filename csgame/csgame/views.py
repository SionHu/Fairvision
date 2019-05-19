from django.http import *
from django.shortcuts import render_to_response,redirect,render


def profile(request):
    return render(request, 'profile.html')

def over(request):
    return render(request, 'over.html')

def about(request):
    return render(request, 'about.html')

def handler404(request, *args, **argv):
    return render(request, '404.html')

def handler500(request, *args, **argv):
    return render(request, '500.html')
