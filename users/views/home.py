from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    assignment = request.GET.get('assignment')
    is_mturker = assignment not in (None, 'ASSIGNMENT_ID_NOT_AVAILABLE')
    print(is_mturker)

    if is_mturker:
        request.session['assignment'] = assignment

    if request.session.get('assignment'):
        messages.info(request, 'Thank you for choosing our project. Your assignment ID is %s.' % (assignment,))
    else:
        messages.warning(request, 'You are not an MTurker.')
    return render(request, 'home.html', {'assignment': assignment if is_mturker else None})
