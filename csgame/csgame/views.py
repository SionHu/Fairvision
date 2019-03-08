from django.http import *
from django.shortcuts import render_to_response,redirect,render

def profile(request):
    return render(request, 'registration/profile.html')
