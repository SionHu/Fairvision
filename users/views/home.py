from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views.decorators.clickjacking import xframe_options_exempt

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

@xframe_options_exempt
def home(request):
    return render(request, 'home.html')
