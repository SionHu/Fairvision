from collections import defaultdict
from csgame.views import over, feedback
from datetime import datetime
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.http import Http404
from django.shortcuts import redirect
from functools import wraps
from .models import HIT
from urllib.parse import urlparse, urlencode
import uuid


NUMROUNDS = settings.NUMROUNDS
ROUNDSMAX = {k:1 if k == 'phase01b' else v for k, v in NUMROUNDS.items()}
# ROUNDSMAX = {'step01':3, 'step02':1, 'step03':1}

def player_required(func):
    '''
    Decorator for views that checks that the logged in user is a mturk worker, or staff
    redirects to the log-in page if necessary.
    '''
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        assignmentId = request.GET.get('assignmentId')

        print("numround: ", NUMROUNDS)

        if assignmentId is not None and assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE':
            hitObj = HIT.objects.only('data').get_or_create(assignment_id=assignmentId, defaults={'data': {'startTime': datetime.now()}})[0]
            request.hit = hitObj.data

            roundnums = request.hit.setdefault('roundnums', {})

            numInPhase = roundnums.get(func.__name__, 0) # this line is pretty unsafe, but it will do

            # increment roundsnum by 1
            if request.method == 'POST':
                roundnums[func.__name__] = numInPhase + 1
                request.hit['hitId'] = request.GET['hitId']
                request.hit['workerId'] = request.GET['workerId']
                hitObj.save()

            # either pay the worker or move onto the next round
            if numInPhase >= ROUNDSMAX[func.__name__]:
                return feedback(request)
            else:
                return func(request, *args, **kwargs)

        elif request.user.is_staff or request.user.is_superuser:
            assignmentId = f"{request.user.username}__{uuid.uuid4().hex}"[:31]
            hitId = 'admin'
            workerId = 'admin'
            return redirect(f"{request.path_info}?assignmentId={assignmentId}&hitId={hitId}&workerId={workerId}&turkSubmitTo=")
        elif assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            return func(request, *args, previewMode=True, **kwargs)
        else:
            raise Http404
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
