from datetime import datetime
from django.conf import settings
from django.http import *
from django.shortcuts import render_to_response,redirect,render
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from users.models import HIT, Question
from users.forms import ContactForm
# from django.contrib.auth.forms import UserCreationForm
import requests


def profile(request):
    return render(request, 'profile.html')

def over(request, phase=None):
    if 'assignmentId' in request.GET:
        hitObj = HIT.objects.only('data').get_or_create(assignment_id=request.GET['assignmentId'], defaults={'data': {}})[0]
        request.hit = hitObj.data
        output = render(request, 'over.html', {'phase': phase, 'roundNums': request.hit.get('roundnums', {}).get(phase)})
        output.set_cookie('assignmentId', request.GET['assignmentId'])
        turkUrl = "https://workersandbox.mturk.com" if x is "" else request.GET['turkSubmitTo']
        output.set_cookie('submissionUrl', turkUrl)
    else:
        output = render(request, 'over.html', {'phase': phase, 'roundNums': 0})
        output.set_cookie("assignmentId", 'None')
        turkUrl = "https://workersandbox.mturk.com" if x is "" else request.GET['turkSubmitTo']
        output.set_cookie('submissionUrl', turkUrl)
    return output

def feedback(request):
    hitObj = HIT.objects.only('data').get_or_create(assignment_id=request.COOKIES['assignmentId'], defaults={'data': {}})[0]
    request.hit = hitObj.data
    request.hit['endTime'] = datetime.now()
    hitObj.save()
    return render(request, 'feedback.html')

def about(request):
    return render(request, 'about.html', {'title': 'About'})

def publication(request):
    return render(request, 'publication.html', {'title': 'Publication'})

def service(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(name+":"+subject, message, from_email, ['yu872@purdue.edu'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            form.save()
            messages.success(request, 'Request sent!')
            return redirect('service')
    return render(request, 'service.html', {'form': form, 'title': 'Service'})

def serviceindex(request):
    return render(request, 'service-index.html')

def handler404(request, *args, **argv):
    return render(request, '404.html', status=404)

def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)

def phase01b(request):
    return render(request, 'phase01b.html')

def stop(request):
    return render(request, 'stop.html')
