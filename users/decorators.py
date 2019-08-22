from collections import defaultdict
from csgame.views import over
from datetime import datetime
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from functools import wraps
from .models import HIT
from urllib.parse import urlparse, urlencode
import uuid


NUMROUNDS = settings.NUMROUNDS


def player_required(func):
    '''
    Decorator for views that checks that the logged in user is a mturk worker, or staff
    redirects to the log-in page if necessary.
    '''
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        assignmentId = request.GET.get('assignmentId')

        if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            assignmentId = None

        if assignmentId:
            hitObj = HIT.objects.only('data').get_or_create(assignment_id=assignmentId, defaults={'data': {'startTime': datetime.now()}})[0]
            request.hit = hitObj.data

            roundnums = request.hit.setdefault('roundnums', {})

            numInPhase = roundnums.get(func.__name__, 0) # this line is pretty unsafe, but it will do

            if request.method == 'POST':
                roundnums[func.__name__] = numInPhase + 1
                request.hit['hitId'] = request.GET['hitId']
                request.hit['workerId'] = request.GET['workerId']
                hitObj.save()
                return func(request, *args, **kwargs)
            else:
                if numInPhase >= NUMROUNDS[func.__name__]:
                    return over(request, func.__name__)
                else:
                    return func(request, *args, **kwargs)

        elif request.user.is_staff or request.user.is_superuser:
            assignmentId = f"{request.user.username}__{uuid.uuid4().hex}"[:31]
            hitId = 'admin'
            workerId = 'admin'
            return redirect(f"{request.path_info}?assignmentId={assignmentId}&hitId={hitId}&workerId={workerId}&turkSubmitTo=")
        else:
            return func(request, *args, previewMode=True, **kwargs)
    return wrapper


# decorator that will not be used now
def requester_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a player,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or (u.is_active and u.is_requester),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
