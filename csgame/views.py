from datetime import datetime
from django.conf import settings
from django.http import *
from django.shortcuts import render_to_response,redirect,render
from users.models import HIT

def profile(request):
    return render(request, 'profile.html')

def over(request, phase=None):
    if 'assignmentId' in request.GET:
        hitObj = HIT.objects.only('data').get_or_create(assignment_id=request.GET['assignmentId'], defaults={'data': {}})[0]
        request.hit = hitObj.data
        output = render(request, 'over.html', {'phase': phase, 'roundNums': request.hit.get('roundnums', {}).get(phase)})
        output.set_cookie('assignmentid', request.GET['assignmentId'])
        output.set_cookie('submissionUrl', request.GET['turkSubmitTo'])
    else:
        output = render(request, 'over.html', {'phase': phase, 'roundNums': 0})
    return output

def feedback(request):
    hitObj = HIT.objects.only('data').get_or_create(assignment_id=request.COOKIES['assignmentid'], defaults={'data': {}})[0]
    request.hit = hitObj.data
    request.hit['endTime'] = datetime.now()
    hitObj.save()
    return render(request, 'feedback.html')

def about(request):
    return render(request, 'about.html')

def handler404(request, *args, **argv):
    return render(request, '404.html', status=404)

def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)

def phase01b(request):
    return render(request, 'phase01b.html')

def stop(request):
    return render(request, 'stop.html')
