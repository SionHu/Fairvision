from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView

from ..forms import PlayerSignUpForm
from ..models import CustomUser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import player_required

@method_decorator([login_required, player_required], name='dispatch')

class PlayerSignUpView(CreateView):
    model = CustomUser
    form_class = PlayerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'player'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')