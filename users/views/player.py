from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import CreateView

from ..forms import PlayerSignUpForm
from ..models import CustomUser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import player_required


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
        return redirect('home')

@login_required
def downloadExperiment(request):
    if request.user.is_staff:
        from users.admin import ExperimentAdmin
        response = HttpResponse(ExperimentAdmin.exportOneExperiment(None), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment;filename=experiment.xlsx'
        return response
        # with open("out.xlsx", 'wb') as file:
        # 	file.write(ExperimentAdmin.exportOneExperiment(None))
