from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
import threading

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    global load_nlp
    if not load_nlp:
        class NLPThread(threading.Thread):
            def run(self):
                from csgame.nlp_loader import nlp
                print("NLP loaded")
        thread = NLPThread()
        thread.setDaemon(True)
        thread.start()
        load_nlp = True

    return render(request, 'home.html')
load_nlp = False
