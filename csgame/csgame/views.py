from django.http import *
from django.shortcuts import render_to_response,redirect,render

def profile(request):
    return render(request, 'profile.html')

def over(request):
    return render(request, 'over.html')

def about(request):
    return render(request, 'about.html')


def phase02(request):
    return render(request, 'phase02.html')

def phase03(request):
    return render(request, 'phase03.html')
