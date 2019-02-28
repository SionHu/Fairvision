from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from ..forms import DocumentForm, ZipfileForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from ..models import Zipfile


class ZipfileCreateView(CreateView):
    model = Zipfile
    form_class=ZipfileForm
    template_name='document_form.html'
    success_url=reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        zipfiles=Zipfile.objects.all()
        context['zipfiles']=zipfiles
        return context
