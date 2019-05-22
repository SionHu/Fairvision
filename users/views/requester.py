from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView

from ..models import CustomUser
from ..forms import RequesterSignUpForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import requester_required

class RequesterSignUpView(CreateView):
    model = CustomUser
    form_class = RequesterSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'requester'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')